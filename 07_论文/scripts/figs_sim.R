# Figures 1-4 for the formal simulation (section 5.4). Run from 06_正式模拟/:  LANG=en_US.UTF-8 Rscript ../07_论文/scripts/figs_sim.R
# Fig 1  key cell: true breadth vs generation-verification model posterior mean, Chen r, Chen d (random 3,000 careful persons, fixed seed)
# Fig 2  person breadth recovery (median within-dataset r) across the 18 s1 cells: generation-verification model vs grid matching r and d
# Labels: methods are named by what they do (generation-verification model / grid matching), not by author or letter; Times New Roman throughout.
# Fig 3  SBC: ECDF difference of ranks, 13 quantities, 95% simultaneous band for discrete uniform ranks by simulation
#        (Säilynoja, Bürkner & Vehtari, 2022, Stat Comput 32:32; implemented here because the SBC/bayesplot packages are not installed)
# Colours: Apple system palette, blue #007AFF (generation-verification model / careful), red #FF3B30 (Chen / careless), grey #8E8E93, light grey #E5E5EA.
# Fig 4  (a) key cell: posterior mean minus truth by true breadth, with 90% coverage; (b) s3: posterior breadth of careless vs careful
suppressMessages({library(data.table); library(ggplot2); library(patchwork)})
qpdf <- function(filename, width, height, ...) grDevices::quartz(type = "pdf", file = filename, width = width, height = height)
qpng <- function(filename, width, height, ...) grDevices::quartz(type = "png", file = filename, width = width, height = height, dpi = 200, bg = "white")
invisible(qpdf(tempfile(), 7, 5))   # macOS Quartz devices embed system fonts (Times New Roman); Cairo is unavailable here (no XQuartz)
od <- "../07_论文/figs"; dir.create(od, showWarnings = FALSE)
rd <- function(pat, ...) rbindlist(lapply(Sys.glob(pat), fread, colClasses = list(character = "rep"), ...), fill = TRUE)
BLUE <- "#007AFF"; RED <- "#FF3B30"; GREY <- "#8E8E93"; LGREY <- "#E5E5EA"
th <- theme_classic(base_size = 9, base_family = "Times New Roman") + theme(strip.background = element_blank(), strip.text = element_text(face = "bold"))
# APA 7: italic statistical symbols (r, N, J, b, d), Greek upright, no leading zero for quantities bounded by 1, minus sign U+2212.
mns <- function(x) gsub("-", "\u2212", x)
apa0 <- function(x) mns(sub("^(-?)0\\.", "\\1.", formatC(x, format = "f", digits = 2)))
num_lab <- function(x) mns(format(x, trim = TRUE, drop0trailing = TRUE))
cor_lab <- function(x) mns(sub("^(-?)0\\.", "\\1.", format(x, trim = TRUE, drop0trailing = TRUE)))
cells <- as.data.table(jsonlite::fromJSON("cells.json")); cells[, cell := sprintf("c%02d", cell)]
save <- function(p, f, w, h) { ggsave(file.path(od, paste0(f, ".pdf")), p, width = w, height = h, device = qpdf); ggsave(file.path(od, paste0(f, ".png")), p, width = w, height = h, device = qpng) }

# ---- Fig 1
per <- rd("out/s1/c10/person_*.csv"); ch <- rd("out/s1/c10/chen_*.csv"); m <- merge(per, ch, by = c("rep", "person"))[careless == FALSE]
set.seed(20261119); s <- m[sample(.N, 3000)]
lab <- function(x, y) sprintf('italic(r)~"= %s"', apa0(cor(x, y)))
f1 <- function(y, col, ttl, yl, rr, ref = FALSE, jit = 0) {
  p <- ggplot(s, aes(b_true, .data[[y]]))
  if (ref) p <- p + geom_abline(lty = 2, colour = GREY)
  p + geom_jitter(size = .4, alpha = .3, colour = col, height = jit, width = 0) + labs(x = "True breadth (logit)", y = yl, title = ttl) +
    annotate("text", -Inf, Inf, label = rr, parse = TRUE, hjust = -.15, vjust = 1.4, size = 3, colour = col, family = "Times New Roman") +
    scale_x_continuous(labels = num_lab) + th }
p1a <- f1("b_mean", BLUE, "Generation–verification model", "Posterior mean", lab(m$b_true, m$b_mean), ref = TRUE) + scale_y_continuous(labels = num_lab)
p1b <- f1("r_chen", RED, expression("Grid matching: " * italic(r)), expression("Estimated " * italic(r)), lab(m$b_true, m$r_chen), jit = .015) + scale_y_continuous(limits = c(-.05, 1.12), labels = cor_lab)
p1c <- f1("d_chen", RED, expression("Grid matching: " * italic(d)), expression("Estimated " * italic(d)), lab(m$b_true, m$d_chen), jit = .015) + scale_y_continuous(limits = c(-.05, 1.12), labels = cor_lab)
save(p1a + p1b + p1c, "fig1_keycell_recovery", 7.2, 2.6)

# ---- Fig 2
pp <- fread("logs/summary_person.csv"); cs <- fread("logs/summary_chen.csv")
f2 <- merge(merge(pp[study == "s1", .(cell, `Generation–verification model` = r_b)], cs[study == "s1", .(cell, `Grid matching r` = r_chen_b, `Grid matching d` = d_chen_b)], by = "cell"), cells[study == "s1", .(cell, N, J, sigma)], by = "cell")
f2 <- melt(f2, id.vars = c("cell", "N", "J", "sigma"), variable.name = "method", value.name = "r")
f2[, J := factor(paste0('italic(J)~"= ', J, '"'), paste0('italic(J)~"= ', c(12, 24), '"'))]; f2[, N := factor(N, c(50, 100, 200))]
p2 <- ggplot(f2, aes(sigma, r, colour = method, shape = N, group = interaction(method, N))) + geom_hline(yintercept = 0, colour = LGREY) +
  geom_line(linewidth = .4) + geom_point(size = 1.6) + facet_wrap(~J, labeller = label_parsed) + scale_x_continuous(breaks = c(1.5, 2.5, 3.5)) +
  scale_colour_manual(values = c(`Generation–verification model` = BLUE, `Grid matching r` = RED, `Grid matching d` = "#FF9F99"), labels = c("Generation\u2013verification model", expression("Grid matching " * italic(r)), expression("Grid matching " * italic(d)))) +
  scale_shape_manual(values = c(16, 17, 15), labels = c(expression(italic(N) ~ "= 50"), expression(italic(N) ~ "= 100"), expression(italic(N) ~ "= 200"))) + scale_y_continuous(labels = cor_lab) +
  labs(x = "Population SD of breadth (\u03c3)", y = "Correlation with true breadth\n(median over datasets)", colour = NULL, shape = NULL) + th
save(p2, "fig2_recovery_by_cell", 6.5, 3)

# ---- Fig 3
rk <- rd("out/sbc/c00/ranks_*.csv"); L <- rk$L[1]; nS <- rk[, .N, by = variable]$N[1]; zz <- (1:L) / (L + 1)
# ECDF of ranks (0..L) at z_i = i/(L+1): share of ranks < i. Band: Säilynoja et al. (2022) simulation method, 5,000 null samples.
set.seed(1804); gam <- replicate(5000, { cnt <- cumsum(tabulate(sample.int(L + 1, nS, TRUE), L + 1))[1:L]
  min(2 * pmin(pbinom(cnt, nS, zz), 1 - pbinom(cnt - 1, nS, zz))) }); gam <- quantile(gam, .05)
band <- data.table(u = zz, lo = qbinom(gam / 2, nS, zz) / nS - zz, hi = qbinom(1 - gam / 2, nS, zz) / nS - zz)
e <- rk[, .(u = zz, d = sapply(1:L, function(i) mean(rank < i)) - zz), by = variable]
lv <- c("mu", "sigma", "gamma", "kappa", "delta", "tau", "rho", "b_draw[1]", "b_draw[2]", "b_draw[3]", "d_draw[1]", "d_draw[2]", "d_draw[3]")
e[, variable := factor(variable, lv, c('"\u03bc"', '"\u03c3"', '"\u03b3"', '"\u03ba"', '"\u03b4"', '"\u03c4"', '"\u03c1"', "italic(b)[1]", "italic(b)[2]", "italic(b)[3]", "italic(v)[1]", "italic(v)[2]", "italic(v)[3]"))]
cat("SBC: share of ECDF points outside the simultaneous band, per quantity:\n"); print(merge(e, band, by = "u")[, .(outside = mean(d < lo | d > hi)), by = variable])
p3 <- ggplot(e, aes(u, d)) + geom_ribbon(data = band, aes(u, ymin = lo, ymax = hi), inherit.aes = FALSE, fill = LGREY) +
  geom_hline(yintercept = 0, colour = GREY, linewidth = .3) + geom_line(colour = BLUE, linewidth = .45) +
  facet_wrap(~variable, nrow = 2, labeller = label_parsed) + scale_x_continuous(breaks = c(0, .5, 1), labels = c("0", ".5", "1")) + scale_y_continuous(labels = cor_lab) +
  labs(x = "Fractional rank", y = "ECDF difference") + th + theme(strip.text = element_text(face = "plain"))
save(p3, "fig3_sbc", 7.2, 3)

# ---- Fig 4
m[, bin := cut(b_true, seq(-10, 8, 1))]
z <- m[, .(x = mean(b_true), bias = mean(b_mean - b_true), lo = quantile(b_mean - b_true, .05), hi = quantile(b_mean - b_true, .95),
            cover = mean(b_true >= b_q5 & b_true <= b_q95), n = .N), by = bin][n >= 200][order(x)]
p4a <- ggplot(z, aes(x, bias)) + geom_hline(yintercept = 0, colour = GREY, linewidth = .3) + geom_linerange(aes(ymin = lo, ymax = hi), colour = BLUE, alpha = .5) + geom_point(colour = BLUE) +
  geom_text(aes(y = max(hi) + .4, label = apa0(cover)), size = 2.4, family = "Times New Roman") + scale_x_continuous(labels = num_lab) + scale_y_continuous(labels = num_lab) +
  labs(x = "True breadth (logit, 1-unit bins)", y = "Posterior mean \u2212 truth", title = "a  Key cell (numbers: 90% coverage)") + th
p3d <- rd("out/s3/c*/person_*.csv"); p3d <- merge(p3d, cells[study == "s3", .(cell, careless_type = careless, prop)], by = "cell")
p3d[, grp := factor(ifelse(careless, ifelse(careless_type == "random", "Random responders", "Give-up responders"), "Careful responders"),
                    c("Careful responders", "Random responders", "Give-up responders"))]
p3d[, cond := factor(sprintf("%s %d%%", careless_type, round(100 * prop)), c("random 5%", "random 10%", "giveup 5%", "giveup 10%"), c("Random 5%", "Random 10%", "Give-up 5%", "Give-up 10%"))]
p4b <- ggplot(p3d, aes(b_mean, colour = grp, linetype = grp)) + geom_density(adjust = 1.2, key_glyph = "path") + facet_wrap(~cond, nrow = 1) + scale_x_continuous(labels = num_lab) + scale_y_continuous(labels = cor_lab) + scale_colour_manual(values = c(BLUE, RED, RED)) + scale_linetype_manual(values = c("solid", "solid", "22")) +
  labs(x = "Posterior mean breadth", y = "Density", colour = NULL, linetype = NULL, title = "b  Simulation 3 (careless responders)") + th + theme(legend.position = "bottom")
save(p4a / p4b + plot_layout(heights = c(1, 1.1)), "fig4_shrinkage_careless", 7.2, 5.2)
cat("figures written to", normalizePath(od), "\n")
