# Fit one version of the unified model. Args: sample  version(A/B/C/D)  iterations
# Data: stan_<sample>_sum_w.json for A, stan_<sample>_prod_w.json for B-D. Output fit_<sample>_<version>w.rds, logs/fit_<sample>_<version>w.txt
suppressMessages(library(cmdstanr)); library(jsonlite)
a <- commandArgs(TRUE); smp <- a[1]; ver <- a[2]; it <- as.integer(a[3])
d <- fromJSON(paste0("stan_", smp, if (ver == "A") "_sum_w.json" else "_prod_w.json"))
gh <- function(n){ if (n == 1) return(list(x = 0, w = 1)); b <- sqrt(seq_len(n-1)/2); Jm <- matrix(0,n,n); Jm[cbind(1:(n-1),2:n)] <- b; Jm[cbind(2:n,1:(n-1))] <- b
  e <- eigen(Jm, symmetric=TRUE); list(x=e$values*sqrt(2), w=e$vectors[1,]^2) }
use_delta <- as.integer(ver %in% c("C","D")); use_tau <- as.integer(ver == "D")
Q1 <- 16; Q2 <- if (use_tau) 8 else 1; g1 <- gh(Q1); g2 <- gh(Q2)
sd <- list(N=d$N, J=d$J, K=d$K, D=d$D, lo=d$lo, hi=d$hi, C=d$C, pad=d$pad, nsol=d$nsol, yk=d$yk,
           Q1=Q1, x1=g1$x, lw1=log(g1$w), Q2=Q2, x2=as.array(g2$x), lw2=as.array(log(g2$w)),
           use_delta=use_delta, use_tau=use_tau, do_gq=1L, G1=61L, G2=if (use_tau) 21L else 1L)
m <- cmdstan_model("breadth_unified.stan", quiet=TRUE)
fit <- m$sample(data=sd, chains=4, parallel_chains=4, iter_warmup=it, iter_sampling=it, seed=1, refresh=0, show_messages=FALSE)
nm <- paste0(smp, "_", ver, "w"); fit$save_object(paste0("fit_", nm, ".rds"))
sink(paste0("logs/fit_", nm, ".txt")); cat("fit", nm, "Q1", Q1, "Q2", Q2, "iter", it, " time", fit$time()$total, "s\n")
print(as.data.frame(fit$summary(c("mu","sigma","gamma","kappa","delta","tau","rho","p_clamped")))); print(fit$diagnostic_summary()); sink()
