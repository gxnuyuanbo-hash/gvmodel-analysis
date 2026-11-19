# Summarize the formal simulation (studies s1, s3; SBC). Uses the last fit attempt per dataset.
# Output: logs/summary_pop.csv, logs/summary_person.csv, logs/summary_chen.csv, logs/sbc_ranks.pdf, printed tables.
suppressMessages(library(data.table)); options(width = 200)
cells <- jsonlite::fromJSON("cells.json"); cells$cell <- sprintf("c%02d", cells$cell)
rd <- function(pat) { f <- Sys.glob(pat); if (!length(f)) return(NULL); rbindlist(lapply(f, fread, colClasses = list(character = c("rep", "cell"))), fill = TRUE) }
pop <- rd("out/*/c*/pop_*.csv")
if (is.null(pop)) quit()
pop <- pop[pop[, .I[attempt == max(attempt)], by = .(study, cell, rep)]$V1]
setnames(pop, c("5%", "95%"), c("q5", "q95"))
conv <- pop[, .(ok = max(rhat) <= 1.01 & min(ess_bulk, ess_tail) >= 400 & divergent[1] == 0, attempt = attempt[1], time = time[1]), by = .(study, cell, rep)]
cat("Convergence by cell (n datasets, share converged after the refit rule, share refitted, median time s):\n")
print(conv[, .(n = .N, converged = round(mean(ok), 3), refitted = round(mean(attempt == 2), 3), time = round(median(time))), by = .(study, cell)])
ps <- pop[, .(n = .N, r = round(cor(truth, mean), 3), bias = round(mean(mean - truth), 3), rmse = round(sqrt(mean((mean - truth)^2)), 3),
              cover90 = round(mean(truth >= q5 & truth <= q95), 3), width = round(mean(q95 - q5), 3)), by = .(study, cell, variable)]
ps <- merge(ps, as.data.table(cells)[, .(study, cell, N, J, sigma, careless, prop)], by = c("study", "cell"), all.x = TRUE)
fwrite(ps, "logs/summary_pop.csv")
cat("\nPopulation parameters, 90% coverage (flag: outside [.85, .95]):\n")
w <- dcast(ps, study + cell + N + J + sigma + careless + prop ~ variable, value.var = "cover90"); print(w)
per <- rd("out/*/c*/person_*.csv")
if (!is.null(per)) {
  per[, zone := cut(b_true, c(-Inf, -4, -1, 2, Inf), labels = c("< -4", "-4..-1", "-1..2", "> 2"))]
  wr <- per[careless == FALSE, .(rb = cor(b_true, b_mean), rd = cor(d_true, d_mean), err = cor(b_mean - b_true, d_mean - d_true)), by = .(study, cell, rep)]
  pp <- merge(wr[, .(r_b = round(median(rb), 3), r_d = round(median(rd), 3), err_bd = round(median(err), 3)), by = .(study, cell)],
              per[careless == FALSE, .(cover_b = round(mean(b_true >= b_q5 & b_true <= b_q95), 3), cover_d = round(mean(d_true >= d_q5 & d_true <= d_q95), 3)), by = .(study, cell)])
  fwrite(pp, "logs/summary_person.csv"); cat("\nPerson parameters (careful responders; median within-dataset r):\n"); print(pp)
  z <- per[careless == FALSE, .(n = .N, bias = round(mean(b_mean - b_true), 3), cover = round(mean(b_true >= b_q5 & b_true <= b_q95), 3)), by = .(study, cell, zone)]
  fwrite(z, "logs/summary_breadth_zone.csv"); cat("\nBreadth coverage by true-breadth zone:\n"); print(dcast(z, study + cell ~ zone, value.var = "cover"))
  if (any(per$careless)) { cat("\nCareless responders vs others, mean posterior breadth and verification:\n")
    print(per[study == "s3", .(b_mean = round(mean(b_mean), 2), d_mean = round(mean(d_mean), 2)), by = .(cell, careless)]) }
  ch <- rd("out/*/c*/chen_*.csv")
  if (!is.null(ch)) {
    f <- Sys.glob("out/*/c*/chen_*.csv"); ch <- rbindlist(lapply(f, function(x) { y <- fread(x, colClasses = list(character = "rep")); y[, `:=`(study = basename(dirname(dirname(x))), cell = basename(dirname(x)))] }))
    m <- merge(ch, per, by = c("study", "cell", "rep", "person"))
    cc <- function(a, b) if (sd(a, na.rm = TRUE) == 0 || sd(b, na.rm = TRUE) == 0) NA_real_ else cor(a, b, use = "complete.obs")
    cs <- m[careless == FALSE, .(r_chen_b = cc(r_chen, b_true), d_chen_b = cc(d_chen, b_true), r_chen_acc = cc(r_chen, acc), d_chen_acc = cc(d_chen, acc),
                                 D_b = cc(b_mean, b_true), stab = median(stability, na.rm = TRUE), n_est = uniqueN(paste(r_chen, d_chen))), by = .(study, cell, rep)]
    cs <- cs[, lapply(.SD, function(v) round(median(v, na.rm = TRUE), 3)), by = .(study, cell), .SDcols = -"rep"]
    fwrite(cs, "logs/summary_chen.csv"); cat("\nChen grid matching vs model D (median within-dataset r):\n"); print(cs)
  }
}
rk <- rd("out/sbc/c*/ranks_*.csv")
if (!is.null(rk)) {
  cat("\nSBC: chi-square test of uniform ranks (20 bins), per quantity:\n")
  sb <- rk[, { h <- tabulate(pmin(floor(rank / (L[1] + 1) * 20) + 1, 20), 20); .(n = .N, p_unif = round(chisq.test(h)$p.value, 3)) }, by = variable]; print(sb)
  pdf("logs/sbc_ranks.pdf", 10, 6); par(mfrow = c(2, 7), mar = c(3, 3, 2, 1))
  for (v in unique(rk$variable)) { x <- sort(rk[variable == v, rank] / (rk$L[1] + 1)); n <- length(x); e <- ecdf(x)(seq(0, 1, .01)) - seq(0, 1, .01)
    plot(seq(0, 1, .01), e, type = "l", ylim = c(-.15, .15), main = v, xlab = "", ylab = ""); abline(h = 0, col = "grey")
    k <- 1.36 / sqrt(n); abline(h = c(-k, k), lty = 2) }   # KS 95% band (approximate)
  dev.off()
}
