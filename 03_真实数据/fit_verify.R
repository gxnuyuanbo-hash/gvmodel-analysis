suppressMessages(library(cmdstanr)); library(jsonlite)
a <- commandArgs(TRUE); smp <- a[1]; Q <- as.integer(a[2]); it <- as.integer(a[3])
d <- fromJSON(paste0("stan_", smp, ".json"))
gh <- function(n){ b <- sqrt(seq_len(n-1)/2); Jm <- matrix(0,n,n); Jm[cbind(1:(n-1),2:n)] <- b; Jm[cbind(2:n,1:(n-1))] <- b
  e <- eigen(Jm, symmetric=TRUE); list(x=e$values*sqrt(2), w=e$vectors[1,]^2) }
g <- gh(Q)
sd <- list(N=d$N, J=d$J, K=d$K, D=d$D, lo=d$lo, hi=d$hi, C=d$C, pad=d$pad, sol=d$sol, yk=d$yk,
           Q=Q, xq=g$x, logwq=log(g$w), do_gq=1L, Gg=61L)
m <- cmdstan_model("breadth_verify.stan", quiet=TRUE)
fit <- m$sample(data=sd, chains=4, parallel_chains=4, iter_warmup=it, iter_sampling=it, seed=1, refresh=0, show_messages=FALSE)
cat("time", fit$time()$total, "\n")
print(fit$summary(c("mu","sigma","gamma","kappa","delta")))
print(fit$diagnostic_summary())
fit$save_object(paste0("fit_", smp, ".rds"))
