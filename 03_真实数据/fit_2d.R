# Fit model D (breadth_2d.stan). Args: sample(s1/s2/pre)  Q1  Q2  iterations. Writes fit_<s>_2d.rds and logs/fit_<s>_2d.txt
suppressMessages(library(cmdstanr)); library(jsonlite)
a <- commandArgs(TRUE); smp <- a[1]; Q1 <- as.integer(a[2]); Q2 <- as.integer(a[3]); it <- as.integer(a[4])
d <- fromJSON(paste0("stan_", smp, "_prod.json"))
gh <- function(n){ b <- sqrt(seq_len(n-1)/2); Jm <- matrix(0,n,n); Jm[cbind(1:(n-1),2:n)] <- b; Jm[cbind(2:n,1:(n-1))] <- b
  e <- eigen(Jm, symmetric=TRUE); list(x=e$values*sqrt(2), w=e$vectors[1,]^2) }
g1 <- gh(Q1); g2 <- gh(Q2)
sd <- list(N=d$N, J=d$J, K=d$K, D=d$D, lo=d$lo, hi=d$hi, C=d$C, pad=d$pad, nsol=d$nsol, yk=d$yk,
           Q1=Q1, x1=g1$x, lw1=log(g1$w), Q2=Q2, x2=g2$x, lw2=log(g2$w), do_gq=1L, G1=41L, G2=21L)
m <- cmdstan_model("breadth_2d.stan", quiet=TRUE)
fit <- m$sample(data=sd, chains=4, parallel_chains=4, iter_warmup=it, iter_sampling=it, seed=1, refresh=0, show_messages=FALSE)
nm <- paste0(smp, "_2d"); fit$save_object(paste0("fit_", nm, ".rds"))
sink(paste0("logs/fit_", nm, ".txt")); cat("fit", nm, "Q1", Q1, "Q2", Q2, "iter", it, " time", fit$time()$total, "s\n")
print(as.data.frame(fit$summary(c("mu","sigma","gamma","kappa","delta","tau","rho","p_clamped")))); print(fit$diagnostic_summary()); sink()
cat(readLines(paste0("logs/fit_", nm, ".txt")), sep="\n")
