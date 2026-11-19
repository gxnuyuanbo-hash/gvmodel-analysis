# Model D parameters for experiment 1 without S1_79 (fit_s1x_Dw.rds). Output: logs/params_Dw_s1x.txt
suppressMessages({library(cmdstanr); library(posterior)})
f <- readRDS("fit_s1x_Dw.rds")
s <- f$summary(c("mu","sigma","gamma","kappa","delta","tau","rho","p_clamped"), "mean", ~quantile(.x, c(.05,.95)))
sink("logs/params_Dw_s1x.txt"); print(as.data.frame(s), digits = 3); sink(); print(as.data.frame(s), digits = 3)
