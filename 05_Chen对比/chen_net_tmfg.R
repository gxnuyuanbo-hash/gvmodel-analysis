# Rebuild Chen et al.'s item networks from their OSF matrices (path_wu/wu_k.xlsx, cosine similarity, diag = 1) with TMFG
# (NetworkToolbox), two ways: (a) similarity as weights, (b) distance 1 - cos as weights, as the paper's text states.
# Saves edge lists for the spreading analysis and reports what each filter keeps.
suppressMessages({library(NetworkToolbox); library(readxl)})
B <- "../01_数据/Chen2026_网络/unzipped/path_wu/"; dir.create("chen_nets", showWarnings = FALSE)
res <- list()
for (k in 0:79) {
  m <- as.data.frame(read_excel(paste0(B, "wu_", k, ".xlsx"))); W <- as.matrix(m[, -1]); W[is.na(W)] <- 0
  diagok <- all(abs(diag(W) - 1) < 1e-6); diag(W) <- 0
  A_s <- suppressMessages(TMFG(W)$A); A_d <- suppressMessages(TMFG(1 - W - diag(nrow(W)))$A)   # distance, zero diagonal
  es <- which(upper.tri(A_s) & A_s != 0, arr.ind = TRUE); ed <- which(upper.tri(A_d) & A_d != 0, arr.ind = TRUE)
  write.csv(data.frame(i = es[, 1] - 1, j = es[, 2] - 1, w = A_s[es]), sprintf("chen_nets/sim_%02d.csv", k), row.names = FALSE)
  write.csv(data.frame(i = ed[, 1] - 1, j = ed[, 2] - 1, w = A_d[ed]), sprintf("chen_nets/dist_%02d.csv", k), row.names = FALSE)
  key <- function(e) paste(e[, 1], e[, 2])
  res[[k + 1]] <- data.frame(item = k, n = nrow(W), diag1 = diagok, all_cos_mean = mean(W[upper.tri(W)]),
    cos_kept_sim = mean(W[es]), cos_kept_dist = mean(W[ed]), edge_overlap = length(intersect(key(es), key(ed))) / nrow(es))
}
r <- do.call(rbind, res); write.csv(r, "chen_nets/tmfg_summary.csv", row.names = FALSE)
cat("items:", nrow(r), "| nodes per item:", min(r$n), "-", max(r$n), "| all diagonals = 1:", all(r$diag1), "\n")
cat("mean cosine of all pairs:", round(mean(r$all_cos_mean), 3), "\n")
cat("mean cosine of edges kept, similarity weights:", round(mean(r$cos_kept_sim), 3), "| distance weights:", round(mean(r$cos_kept_dist), 3), "\n")
cat("share of similarity-TMFG edges also kept by distance-TMFG:", round(mean(r$edge_overlap), 3), "\n")
