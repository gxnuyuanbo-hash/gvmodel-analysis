# Fit model D (breadth_unified.stan, use_delta = use_tau = 1) to one simulated dataset; save compact summaries only.
# Arg: dataset index. Output: out/pop_<r>.csv (population parameters vs truth), out/person_<r>.csv (b and d per person).
suppressMessages({library(cmdstanr); library(jsonlite); library(posterior)})
r <- sprintf("%03d", as.integer(commandArgs(TRUE)[1])); if (file.exists(paste0("out/pop_", r, ".csv"))) quit()
d <- fromJSON(paste0("data/sim_", r, ".json")); tr <- fromJSON(paste0("data/truth_", r, ".json"))
gh <- function(n){ b <- sqrt(seq_len(n-1)/2); Jm <- matrix(0,n,n); Jm[cbind(1:(n-1),2:n)] <- b; Jm[cbind(2:n,1:(n-1))] <- b
  e <- eigen(Jm, symmetric=TRUE); list(x=e$values*sqrt(2), w=e$vectors[1,]^2) }
g1 <- gh(16); g2 <- gh(8)
sd <- list(N=d$N, J=d$J, K=d$K, D=d$D, lo=d$lo, hi=d$hi, C=d$C, pad=d$pad, nsol=d$nsol, yk=d$yk,
           Q1=16, x1=g1$x, lw1=log(g1$w), Q2=8, x2=g2$x, lw2=log(g2$w), use_delta=1L, use_tau=1L, do_gq=1L, G1=61L, G2=21L)
m <- cmdstan_model("../03_真实数据/breadth_unified.stan", quiet=TRUE)
fit <- m$sample(data=sd, chains=4, parallel_chains=4, iter_warmup=500, iter_sampling=500, seed=as.integer(r)+1, refresh=0, show_messages=FALSE)
pv <- c("mu","sigma","gamma","kappa","delta","tau","rho")
s <- as.data.frame(fit$summary(pv, "mean", ~quantile(.x, c(.05, .95)), "rhat", "ess_bulk", "ess_tail"))
s$truth <- unlist(tr[pv]); s$dataset <- r; s$divergent <- sum(fit$diagnostic_summary()$num_divergent); s$time <- fit$time()$total
write.csv(s, paste0("out/pop_", r, ".csv"), row.names=FALSE)
q <- function(v) { x <- fit$draws(v, format="draws_matrix"); data.frame(mean=colMeans(x), q5=apply(x,2,quantile,.05), q95=apply(x,2,quantile,.95)) }
b <- q("b_draw"); dd <- q("d_draw")
write.csv(data.frame(dataset=r, person=seq_len(d$N), b_true=tr$b, b_mean=b$mean, b_q5=b$q5, b_q95=b$q95,
                     d_true=tr$d, d_mean=dd$mean, d_q5=dd$q5, d_q95=dd$q95), paste0("out/person_", r, ".csv"), row.names=FALSE)
