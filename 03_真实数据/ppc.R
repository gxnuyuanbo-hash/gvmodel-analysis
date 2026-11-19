suppressMessages(library(cmdstanr)); library(jsonlite); library(posterior)
for (smp in strsplit(Sys.getenv("SMPS","s1 s2 pre")," ")[[1]]) {
  d <- fromJSON(paste0("stan_", sub("_2d$", "_prod", smp), ".json")); fit <- readRDS(paste0("fit_", smp, ".rds"))
  N <- d$N; J <- d$J; ns <- d$nsol; yk <- d$yk
  cor_of <- function(y) { m <- matrix(NA, N, J); for (j in 1:J) m[, j] <- ifelse(y[, j] < 0, NA, as.integer(y[, j] >= 1 & y[, j] <= ns[j])); m }
  na_of  <- function(y) { m <- matrix(NA, N, J); for (j in 1:J) m[, j] <- ifelse(y[, j] < 0, NA, as.integer(y[, j] == 0)); m }
  oc <- cor_of(yk); on <- na_of(yk)
  yr <- fit$draws("yrep", format = "draws_matrix"); S <- 400; sel <- sample(nrow(yr), S)
  pi_acc <- matrix(0, S, J); pi_na <- matrix(0, S, J); psd <- numeric(S); pp <- matrix(0, S, N)
  for (s in 1:S) { y <- matrix(as.integer(yr[sel[s], ]), N, J); y[yk < 0] <- -1
    c <- cor_of(y); pi_acc[s, ] <- colMeans(c, na.rm = TRUE); pi_na[s, ] <- colMeans(na_of(y), na.rm = TRUE)
    pp[s, ] <- rowMeans(c, na.rm = TRUE); psd[s] <- sd(pp[s, ]) }
  lt <- fit$draws(if ("b_draw" %in% fit$metadata()$stan_variables) "b_draw" else "lt_draw", format = "draws_matrix"); pm <- colMeans(lt); pv <- apply(lt, 2, var)
  pacc <- rowMeans(oc, na.rm = TRUE)
  cat("\n==", smp, " N", N, "\n")
  cat("overall acc obs", round(mean(oc, na.rm=T),3), "pred", round(mean(pi_acc),3),
      "| no-answer obs", round(mean(on, na.rm=T),3), "pred", round(mean(pi_na),3), "\n")
  cat("item acc r(obs,pred)", round(cor(colMeans(oc, na.rm=T), colMeans(pi_acc)),3),
      " item no-answer r", round(cor(colMeans(on, na.rm=T), colMeans(pi_na)),3), "\n")
  cat("SD person acc obs", round(sd(pacc),3), "pred 90% [", round(quantile(psd, c(.05,.95), na.rm=TRUE),3), "]\n")
  cat("breadth reliability (var(pm)/(var(pm)+mean pv))", round(var(pm)/(var(pm)+mean(pv)),3),
      " r(breadth, person acc)", round(cor(pm, pacc),3), "\n")
}
