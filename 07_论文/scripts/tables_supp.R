# Supplementary tables S2 (simulation 3, careless responders) and S3 (simulation 1, all 18 cells).
# Run from 06_正式模拟/:  LANG=en_US.UTF-8 Rscript ../07_论文/scripts/tables_supp.R
# Inputs: logs/summary_pop.csv, summary_person.csv, summary_chen.csv, summary_breadth_zone.csv (from summarize_sim.R),
#         out/*/c*/pop_*.csv (convergence), out/s3/c*/person_*.csv (careless-responder rows).
# Output: ../07_论文/supp/S2*.csv (simulation 3), S3*.csv (simulation 1) and ../07_论文/supp/补充材料_S2_S3.md
suppressMessages(library(data.table))
od <- "../07_论文/supp"; dir.create(od, showWarnings = FALSE)
cells <- as.data.table(jsonlite::fromJSON("cells.json")); cells[, cell := sprintf("c%02d", cell)]
pop <- fread("logs/summary_pop.csv", colClasses = list(character = "cell")); per <- fread("logs/summary_person.csv")
chn <- fread("logs/summary_chen.csv"); zon <- fread("logs/summary_breadth_zone.csv")
rd <- function(pat) rbindlist(lapply(Sys.glob(pat), fread, colClasses = list(character = c("rep", "cell"))), fill = TRUE)
pv <- c("mu", "sigma", "gamma", "kappa", "delta", "tau", "rho")
f2 <- function(x) sub("^(-?)0\\.", "\\1.", sprintf("%.2f", x))   # APA style: no leading zero
f3 <- function(x) sub("^(-?)0\\.", "\\1.", sprintf("%.3f", x))

# convergence (last attempt per dataset)
pp <- rd("out/*/c*/pop_*.csv"); pp <- pp[pp[, .I[attempt == max(attempt)], by = .(study, cell, rep)]$V1]
cv <- pp[, .(ok = max(rhat) <= 1.01 & min(ess_bulk, ess_tail) >= 400 & divergent[1] == 0, refit = attempt[1] == 2, time = time[1]), by = .(study, cell, rep)]
cv <- cv[, .(n_rep = .N, converged = mean(ok), refitted = mean(refit), time_min = median(time) / 60), by = .(study, cell)]

design <- cells[, .(study, cell, N, J, sigma, careless, prop)]
md <- c("# 补充材料 S2–S3", "",
        sprintf("由 `07_论文/scripts/tables_supp.R` 生成（%s）。所有数值来自 `06_正式模拟/logs/` 的汇总文件及逐数据集输出。个人层面相关为数据集内相关在各数据集上的中位数；覆盖率为 90%% 后验区间覆盖真值的比例。", Sys.Date()), "")
mdtab <- function(d, title, note) {
  h <- paste0("| ", paste(names(d), collapse = " | "), " |"); s <- paste0("|", paste(rep("---", ncol(d)), collapse = "|"), "|")
  b <- apply(d, 1, function(r) paste0("| ", paste(r, collapse = " | "), " |"))
  c(paste0("### ", title), "", h, s, b, "", paste0("*注*：", note), "") }

# ---------------- S3: simulation 1, 18 cells
s1 <- design[study == "s1"][order(N, J, sigma)]
lab <- s1[, .(cell, N, J, sigma)]
# S3a population parameters: bias and 90% coverage
pa <- pop[study == "s1", .(cell, variable, bias, rmse, cover90, width)]
fwrite(merge(lab, pa, by = "cell")[order(N, J, sigma, match(variable, pv))], file.path(od, "S3a_population_long.csv"))
w <- dcast(pa, cell ~ variable, value.var = c("bias", "cover90"))
t2a <- merge(lab, w, by = "cell")[order(N, J, sigma)]
t2a_md <- t2a[, c(list(N = N, J = J, `σ` = sigma), setNames(lapply(pv, function(v) sprintf("%s (%s)", f2(get(paste0("bias_", v))), f2(get(paste0("cover90_", v))))), pv))]
md <- c(md, "## S3 模拟 1：18 个格子的完整结果", "",
        mdtab(t2a_md, "表 S3a 总体参数：偏差（90% 覆盖率）",
              "每格 200 个数据集（N = 100, J = 24, σ = 2.5 的关键格为 1,000 个）。偏差 = 后验均值 − 真值。均方根误差与区间宽度见 `S3a_population_long.csv`。"))
# S3b person-level recovery and breadth coverage by zone
zw <- dcast(zon[study == "s1"], cell ~ zone, value.var = "cover")
t2b <- Reduce(function(a, b) merge(a, b, by = "cell"), list(lab, per[study == "s1", .(cell, r_b, r_d, cover_b, cover_d, err_bd)], zw))[order(N, J, sigma)]
fwrite(t2b, file.path(od, "S3b_person.csv"))
t2b_md <- t2b[, .(N, J, `σ` = sigma, `r(b)` = f2(r_b), `r(d)` = f2(r_d), `覆盖 b` = f2(cover_b), `覆盖 d` = f2(cover_d), `误差相关 b,d` = f2(err_bd),
                  `b < −4` = f2(`< -4`), `−4 ≤ b < −1` = f2(`-4..-1`), `−1 ≤ b < 2` = f2(`-1..2`), `b ≥ 2` = f2(`> 2`))]
md <- c(md, mdtab(t2b_md, "表 S3b 个人参数恢复（认真作答者）",
                  "r(b)、r(d)：真值与后验均值的数据集内相关（中位数）。误差相关：b 与 d 估计误差的相关。右侧四列为按真实广度分区的 b 的 90% 覆盖率。"))
# S3c grid matching and convergence
t2c <- Reduce(function(a, b) merge(a, b, by = "cell"), list(lab, chn[study == "s1"], cv[study == "s1", .(cell, n_rep, converged, refitted, time_min)]))[order(N, J, sigma)]
fwrite(t2c, file.path(od, "S3c_gridmatching_convergence.csv"))
t2c_md <- t2c[, .(N, J, `σ` = sigma, `r(r̂, b)` = f2(r_chen_b), `r(d̂, b)` = f2(d_chen_b), `r(r̂, 正确率)` = f2(r_chen_acc), `r(d̂, 正确率)` = f2(d_chen_acc),
                  `稳定性` = f2(stab), `不同估计数` = n_est, `数据集` = n_rep, `收敛` = f2(converged), `重拟合` = f2(refitted), `时间 (min)` = sprintf("%.1f", time_min))]
md <- c(md, mdtab(t2c_md, "表 S3c 网格匹配估计与生成–验证模型的收敛",
                  "r̂、d̂：网格匹配在同一数据上的个人估计。稳定性：网格匹配的稳定性指标（数据集中位数）。不同估计数：一个数据集内出现的不同 (r̂, d̂) 组合数的中位数。收敛：R̂ ≤ 1.01、ESS ≥ 400 且无发散转移的比例（应用重拟合规则后）。时间为单个数据集拟合时间的中位数。"))

# ---------------- S2: simulation 3, careless responders
s3 <- design[study == "s3"]; s3[, cond := sprintf("%s %d%%", ifelse(careless == "random", "随机作答", "放弃作答"), round(100 * prop))]
base <- data.table(cell = "c10", cond = "无粗心作答（关键格）")
cl <- rbind(base, s3[, .(cell, cond)])
key <- function(st, ce) paste(st, ce)
popx <- pop[key(study, cell) %in% c("s1 c10", paste("s3", s3$cell))]; popx[, cond := cl$cond[match(cell, cl$cell)]]; popx[study == "s1", cond := base$cond]
popx[study == "s3", cond := s3$cond[match(cell, s3$cell)]]
fwrite(popx[, .(cond, variable, bias, rmse, cover90, width)][order(match(cond, cl$cond), match(variable, pv))], file.path(od, "S2a_population_long.csv"))
w1 <- dcast(popx, cond ~ variable, value.var = c("bias", "cover90"))[order(match(cond, c(base$cond, s3$cond)))]
t1a_md <- w1[, c(list(`条件` = cond), setNames(lapply(pv, function(v) sprintf("%s (%s)", f2(get(paste0("bias_", v))), f2(get(paste0("cover90_", v))))), pv))]
md <- c(md, "## S2 模拟 3：粗心作答者", "",
        mdtab(t1a_md, "表 S2a 总体参数：偏差（90% 覆盖率）",
              "每个条件 200 个数据集，N = 100，J = 24，σ = 2.5；第一行为模拟 1 的关键格（1,000 个数据集）作为对照。随机作答者每题在“不作答”和全部候选词中均匀随机选择；放弃作答者每题以 .9 的概率不作答，其余按模型作答。总体参数的真值为认真作答者所来自的总体。"))
# S2b person level by group
p3 <- rd("out/s3/c*/person_*.csv"); p3 <- merge(p3, s3[, .(cell, cond)], by = "cell")
g <- p3[, .(n = .N, b_true = mean(b_true), b_mean = mean(b_mean), b_bias = mean(b_mean - b_true), cover_b = mean(b_true >= b_q5 & b_true <= b_q95),
            d_true = mean(d_true), d_mean = mean(d_mean), d_bias = mean(d_mean - d_true), cover_d = mean(d_true >= d_q5 & d_true <= d_q95)), by = .(cell, cond, careless)]
# where careless responders sit in the within-dataset distribution of posterior breadth
# detection: careless share among the k most extreme posterior breadths in the expected direction (k = number of careless responders in the dataset)
pr <- merge(p3, s3[, .(cell, careless_type = careless)], by = "cell")[, .(careless, pct = frank(b_mean) / .N,
            top = if (careless_type[1] == "random") frank(-b_mean, ties.method = "first") <= sum(careless) else frank(b_mean, ties.method = "first") <= sum(careless)), by = .(cell, rep)]
pr <- pr[careless == TRUE, .(pct_b = mean(pct), extreme = mean(top)), by = cell]
g <- merge(g, pr[, .(cell, careless = TRUE, pct_b, extreme)], by = c("cell", "careless"), all.x = TRUE)
rr <- per[study == "s3", .(cell, careless = FALSE, r_b, r_d)]; g <- merge(g, rr, by = c("cell", "careless"), all.x = TRUE)
g <- g[order(cell, careless)]; fwrite(g, file.path(od, "S2b_person_by_group.csv"))
na <- function(x, f) ifelse(is.na(x), "—", f(x))
t1b_md <- g[, .(`条件` = cond, `组别` = ifelse(careless, "粗心", "认真"), `人次` = format(n, big.mark = ","), `b 真值均值` = f2(b_true), `b 后验均值` = f2(b_mean), `b 偏差` = f2(b_bias), `覆盖 b` = f2(cover_b),
                `d 真值均值` = f2(d_true), `d 后验均值` = f2(d_mean), `d 偏差` = f2(d_bias), `覆盖 d` = f2(cover_d), `r(b)` = na(r_b, f2), `r(d)` = na(r_d, f2), `b 百分位` = na(pct_b, f2), `检出率` = na(extreme, f2))]
md <- c(md, mdtab(t1b_md, "表 S2b 个人参数：认真作答者与粗心作答者",
                  "粗心作答者的 b、d 真值从同一总体抽取，但其作答不由这些参数生成，因此其偏差和覆盖率反映的是估计被推向何处。r(b)、r(d) 只对认真作答者计算（数据集内相关的中位数）。b 百分位：粗心作答者的后验广度在本数据集全部被试中的平均百分位。检出率：设一个数据集中有 k 名粗心作答者，按后验广度取最高（随机作答）或最低（放弃作答）的 k 人，其中粗心作答者所占比例的均值。"))
# S2c grid matching under careless responding
t1c <- merge(s3[, .(cell, cond)], chn[study == "s3"], by = "cell"); fwrite(t1c, file.path(od, "S2c_gridmatching.csv"))
md <- c(md, mdtab(t1c[, .(`条件` = cond, `r(r̂, b)` = f2(r_chen_b), `r(d̂, b)` = f2(d_chen_b), `r(r̂, 正确率)` = f2(r_chen_acc), `r(d̂, 正确率)` = f2(d_chen_acc), `生成–验证模型 r(b)` = f2(D_b), `稳定性` = f2(stab), `不同估计数` = n_est)],
                  "表 S2c 粗心作答条件下的网格匹配估计", "只对认真作答者计算，数值为数据集内相关的中位数。"))
writeLines(md, file.path(od, "补充材料_S2_S3.md")); cat("written:", normalizePath(od), "\n"); print(g)
