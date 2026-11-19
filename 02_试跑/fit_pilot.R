suppressMessages({library(cmdstanr); library(jsonlite)})
args <- commandArgs(TRUE); tag <- if (length(args)) args[1] else "pilot"
d <- fromJSON("pilot_data.json", simplifyVector = TRUE)
tr <- fromJSON("pilot_truth.json")
J <- d$J; K <- d$K; G <- d$G
Larr <- array(unlist(d$L), dim = c(G, K, J))   # fromJSON fills column-major; check below
# rebuild as list J x K of vectors G in correct order
Lraw <- d$L                                     # J x K x G array from simplifyVector
dat <- list(N = d$N, J = J, K = K, G = G, grid = d$grid,
            L = Lraw, y = d$y)
mod <- cmdstan_model("breadth.stan", quiet = TRUE)
t0 <- Sys.time()
fit <- mod$sample(data = dat, chains = 4, parallel_chains = 4, iter_warmup = 500, iter_sampling = 500,
                  refresh = 0, show_messages = FALSE, seed = 11)
el <- as.numeric(difftime(Sys.time(), t0, units = "secs"))
s <- fit$summary(c("mu", "sigma", "gamma", "kappa"))
lt <- fit$summary("lt")
diag <- fit$diagnostic_summary(quiet = TRUE)
cat(sprintf("[%s] wall %.1f s | max Rhat %.3f | min ESS_bulk %.0f | divergences %d\n", tag, el,
            max(fit$summary()$rhat, na.rm = TRUE), min(fit$summary()$ess_bulk, na.rm = TRUE), sum(diag$num_divergent)))
print(s[, c("variable", "mean", "q5", "q95", "rhat")])
cat(sprintf("truth: mu %.2f sigma %.2f gamma %.2f kappa %.2f\n", tr$mu, tr$sigma, tr$gamma, tr$kappa))
cat(sprintf("person breadth recovery: r = %.3f | 90%% coverage = %.2f\n", cor(lt$mean, tr$logit_theta),
            mean(tr$logit_theta >= lt$q5 & tr$logit_theta <= lt$q95)))
