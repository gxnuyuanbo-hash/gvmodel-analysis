# Fit model D to one simulated dataset of the formal simulation. Usage: Rscript fit_cell.R <study> <cell> <rep>
# Settings: 4 chains x 750 + 750, Q1 = 16, Q2 = 8, G1 = 61, G2 = 21 (as in the pilot). If max Rhat > 1.01, min bulk or tail
# ESS < 400, or any divergence, refit once with 1,500 + 1,500 and keep both summaries (attempt = 1, 2); results use the last.
# Study "sbc" uses breadth_unified_sbc.stan (prior-matched) and also stores SBC ranks.
# Outputs (skipped if present): out/<study>/c<cell>/pop_<rep>.csv, person_<rep>.csv, and for sbc ranks_<rep>.csv.
suppressMessages({library(cmdstanr); library(jsonlite); library(posterior)})
a <- commandArgs(TRUE); study <- a[1]; cell <- sprintf("c%02d", as.integer(a[2])); rep <- sprintf("%04d", as.integer(a[3]))
od <- file.path("out", study, cell); dir.create(od, recursive = TRUE, showWarnings = FALSE)
if (file.exists(file.path(od, paste0("pop_", rep, ".csv")))) quit()
dd <- file.path("data", study, cell); d <- fromJSON(file.path(dd, paste0("sim_", rep, ".json"))); tr <- fromJSON(file.path(dd, paste0("truth_", rep, ".json")))
gh <- function(n){ b <- sqrt(seq_len(n-1)/2); Jm <- matrix(0,n,n); Jm[cbind(1:(n-1),2:n)] <- b; Jm[cbind(2:n,1:(n-1))] <- b
  e <- eigen(Jm, symmetric=TRUE); list(x=e$values*sqrt(2), w=e$vectors[1,]^2) }
g1 <- gh(16); g2 <- gh(8)
sd <- list(N=d$N, J=d$J, K=d$K, D=d$D, lo=d$lo, hi=d$hi, C=d$C, pad=d$pad, nsol=as.array(d$nsol), yk=d$yk,
           Q1=16, x1=g1$x, lw1=log(g1$w), Q2=8, x2=g2$x, lw2=log(g2$w), use_delta=1L, use_tau=1L, do_gq=1L, G1=61L, G2=21L)
stanfile <- if (study == "sbc") "breadth_unified_sbc.stan" else "../03_真实数据/breadth_unified.stan"
m <- cmdstan_model(stanfile, quiet = TRUE)
it <- as.integer(Sys.getenv("ITER", "750")); pv <- c("mu","sigma","gamma","kappa","delta","tau","rho")
seed <- as.integer(sum(utf8ToInt(study)) * 1e5 + as.integer(a[2]) * 1e4 + as.integer(a[3]))
summ <- list()
for (attempt in 1:2) {
  fit <- m$sample(data=sd, chains=4, parallel_chains=4, iter_warmup=it*attempt, iter_sampling=it*attempt, seed=seed+attempt,
                  refresh=0, show_messages=FALSE)
  s <- as.data.frame(fit$summary(pv, "mean", ~quantile(.x, c(.05, .95)), "rhat", "ess_bulk", "ess_tail"))
  s$truth <- unlist(tr[pv]); s$study <- study; s$cell <- cell; s$rep <- rep; s$attempt <- attempt
  s$divergent <- sum(fit$diagnostic_summary()$num_divergent); s$time <- fit$time()$total
  s$p_clamped <- mean(fit$draws("p_clamped"))
  summ[[attempt]] <- s
  if (max(s$rhat) <= 1.01 && min(s$ess_bulk, s$ess_tail) >= 400 && s$divergent[1] == 0) break
}
write.csv(do.call(rbind, summ), file.path(od, paste0("pop_", rep, ".csv")), row.names = FALSE)
q <- function(v) { x <- fit$draws(v, format="draws_matrix"); data.frame(mean=colMeans(x), q5=apply(x,2,quantile,.05), q95=apply(x,2,quantile,.95)) }
b <- q("b_draw"); dv <- q("d_draw")
write.csv(data.frame(study=study, cell=cell, rep=rep, person=seq_len(d$N), careless=tr$careless, b_true=tr$b, b_mean=b$mean, b_q5=b$q5,
                     b_q95=b$q95, d_true=tr$d, d_mean=dv$mean, d_q5=dv$q5, d_q95=dv$q95), file.path(od, paste0("person_", rep, ".csv")), row.names = FALSE)
if (study == "sbc") {
  # SBC ranks: thin to ~100 draws; rank = #draws < truth, ties broken at random (person b, d come from a grid)
  set.seed(seed); L <- 100; dr <- fit$draws(c(pv, "b_draw[1]", "b_draw[2]", "b_draw[3]", "d_draw[1]", "d_draw[2]", "d_draw[3]"), format="draws_matrix")
  idx <- round(seq(1, nrow(dr), length.out = L)); dr <- dr[idx, , drop = FALSE]
  tv <- c(unlist(tr[pv]), tr$b[1:3], tr$d[1:3])
  rk <- sapply(seq_along(tv), function(k) sum(dr[, k] < tv[k]) + sum(runif(sum(dr[, k] == tv[k])) < .5))
  write.csv(data.frame(rep=rep, variable=colnames(dr), rank=rk, L=L), file.path(od, paste0("ranks_", rep, ".csv")), row.names = FALSE)
}
