# Per-chain means of population parameters, to diagnose non-convergence (multimodality vs slow mixing).
suppressMessages(library(cmdstanr)); library(posterior)
for (n in commandArgs(TRUE)) { f <- readRDS(paste0("fit_", n, ".rds"))
  dr <- f$draws(c("mu","sigma","gamma","kappa","delta","lp__"))
  cat("==", n, "\n"); print(round(apply(dr, c(2, 3), mean), 3))
  cat("cor(mu, sigma) =", round(cor(as.vector(dr[,,"mu"]), as.vector(dr[,,"sigma"])), 2), "\n") }
