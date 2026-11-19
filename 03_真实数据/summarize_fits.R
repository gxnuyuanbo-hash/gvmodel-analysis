# Write convergence + parameter summaries of saved fits to logs/fit_<name>.txt
suppressMessages(library(cmdstanr))
a <- commandArgs(TRUE)
for (n in a) { f <- readRDS(paste0("fit_", n, ".rds")); v <- intersect(c("mu","sigma","gamma","kappa","delta","sigma_d","rho"), f$metadata()$stan_variables)
  sink(paste0("logs/fit_", n, ".txt")); cat("fit", n, " time", f$time()$total, "s\n"); print(as.data.frame(f$summary(v))); print(f$diagnostic_summary()); sink() }
