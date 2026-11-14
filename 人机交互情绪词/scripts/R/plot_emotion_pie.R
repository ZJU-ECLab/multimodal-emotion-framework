#!/usr/bin/env Rscript

if (.Platform$OS.type == "windows") {
  invisible(Sys.setlocale("LC_CTYPE", "English_United States.utf8"))
}

# Draw the Chinese emotion-frequency donut.

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggrepel)
})

script_args <- commandArgs(trailingOnly = FALSE)
script_file <- grep("^--file=", script_args, value = TRUE)
script_file <- if (length(script_file)) sub("^--file=", "", script_file[[1]]) else NULL
script_dir <- if (is.null(script_file)) getwd() else dirname(normalizePath(script_file))
source(file.path(script_dir, "plot_style.R"))
root <- project_root_from_script(script_file)
style <- read_plot_style(root)
emotion_color_map <- read_article_color_map(root)
font_family <- Sys.getenv(
  "HCI_PLOT_FONT",
  if (.Platform$OS.type == "windows") "Microsoft YaHei" else "Noto Sans CJK SC"
)

table_dir <- file.path(root, "outputs", "tables")
figure_dir <- file.path(root, "figures")
dir.create(figure_dir, recursive = TRUE, showWarnings = FALSE)

stats_path <- file.path(table_dir, "emotion_label_statistics.csv")
translation_path <- file.path(root, "data", "raw", "emotion_translations.csv")
if (!file.exists(stats_path)) stop("Missing emotion-label statistics: ", stats_path)
if (!file.exists(translation_path)) stop("Missing reviewed Chinese translations: ", translation_path)

stats <- read.csv(
  stats_path, stringsAsFactors = FALSE, check.names = FALSE,
  fileEncoding = "UTF-8-BOM"
)
translations <- read.csv(
  translation_path, stringsAsFactors = FALSE, check.names = FALSE,
  fileEncoding = "UTF-8-BOM"
)
stats$article_count <- as.integer(stats$article_count)

selected <- stats[stats$article_count >= 5, , drop = FALSE]
selected <- selected[order(-selected$article_count, selected$rank), , drop = FALSE]
if (!nrow(selected)) stop("No emotion labels at the >=5 cutoff")

translation_map <- setNames(translations$preferred_chinese_translation, translations$emotion_label)
missing_translation <- selected$emotion_label[is.na(unname(translation_map[selected$emotion_label]))]
if (length(missing_translation)) {
  stop("Missing Chinese translations for: ", paste(missing_translation, collapse = ", "))
}

excluded <- stats[stats$article_count < 5, , drop = FALSE]
pie_data <- data.frame(
  emotion_label = c(selected$emotion_label, "Other"),
  emotion_label_zh = c(unname(translation_map[selected$emotion_label]), "其他"),
  article_count = c(selected$article_count, sum(excluded$article_count)),
  stringsAsFactors = FALSE
)
pie_data$start <- c(0, head(cumsum(pie_data$article_count), -1))
pie_data$end <- cumsum(pie_data$article_count)
pie_data$mid <- (pie_data$start + pie_data$end) / 2
pie_data$total <- sum(pie_data$article_count)
if (unique(pie_data$total) != sum(stats$article_count)) stop("Pie total does not match source statistics")

sector_angles <- function(start, end, total, radial_steps = 80) {
  theta_start <- pi / 2 - 2 * pi * start / total
  theta_end <- pi / 2 - 2 * pi * end / total
  n_steps <- max(2L, ceiling(abs(theta_end - theta_start) * radial_steps))
  seq(theta_start, theta_end, length.out = n_steps + 1L)
}

annular_polygon <- function(start, end, total, inner_radius, outer_radius, group, label) {
  angles <- sector_angles(start, end, total)
  outer <- data.frame(x = outer_radius * cos(angles), y = outer_radius * sin(angles))
  inner <- data.frame(x = inner_radius * cos(rev(angles)), y = inner_radius * sin(rev(angles)))
  points <- rbind(outer, inner)
  points$group <- group
  points$emotion_label <- label
  points
}

emotion_polygons <- do.call(rbind, lapply(seq_len(nrow(pie_data)), function(i) {
  annular_polygon(
    pie_data$start[i], pie_data$end[i], pie_data$total[i],
    inner_radius = 0.28, outer_radius = 1.0,
    group = pie_data$emotion_label[i], label = pie_data$emotion_label[i]
  )
}))

fill_values <- c(
  emotion_color_map[pie_data$emotion_label[-nrow(pie_data)]],
  Other = style$colors[["frequency.under-5"]]
)

rgb <- grDevices::col2rgb(fill_values[pie_data$emotion_label]) / 255
luminance <- 0.2126 * rgb[1, ] + 0.7152 * rgb[2, ] + 0.0722 * rgb[3, ]
pie_data$text_colour <- ifelse(luminance < 0.58, "#FFFFFF", style$colors[["text.primary"]])

# Put labels near the outer, wider end of each sector. The radial orientation
# follows the line from the outside of the circle toward its centre. Text is
# flipped by 180 degrees where needed so it remains upright to the reader.
pie_data$angle <- pi / 2 - 2 * pi * pie_data$mid / pie_data$total
pie_data$radial_angle <- pie_data$angle * 180 / pi
pie_data$radial_angle <- ifelse(
  pie_data$radial_angle < -90,
  pie_data$radial_angle + 180,
  pie_data$radial_angle
)
pie_data$radial_angle <- ifelse(
  pie_data$radial_angle > 90,
  pie_data$radial_angle - 180,
  pie_data$radial_angle
)
pie_data$x <- 0.82 * cos(pie_data$angle)
pie_data$y <- 0.82 * sin(pie_data$angle)
pie_data$outer_x <- 0.98 * cos(pie_data$angle)
pie_data$outer_y <- 0.98 * sin(pie_data$angle)
pie_data$small_sector <- pie_data$article_count < 8 & pie_data$emotion_label != "Other"
pie_data$english_label <- sprintf("%s %d", pie_data$emotion_label, pie_data$article_count)
pie_data$chinese_label <- sprintf("%s %d", pie_data$emotion_label_zh, pie_data$article_count)

label_size <- function(article_count, language) {
  if (language == "zh") {
    ifelse(article_count >= 30, 4.9,
      ifelse(article_count >= 20, 4.5,
        ifelse(article_count >= 10, 4.0, 3.4)
      )
    )
  } else {
    ifelse(article_count >= 30, 4.6,
      ifelse(article_count >= 20, 4.2,
        ifelse(article_count >= 10, 3.7, 3.1)
      )
    )
  }
}

make_pie_plot <- function(data, language = c("en", "zh")) {
  language <- match.arg(language)
  label_field <- if (language == "zh") "chinese_label" else "english_label"
  label_family <- font_family
  data$plot_label <- data[[label_field]]
  data$label_size <- label_size(data$article_count, language)
  in_sector <- data[!data$small_sector, , drop = FALSE]
  callouts <- data[data$small_sector, , drop = FALSE]
  ggplot() +
    geom_polygon(
      data = emotion_polygons,
      aes(x = x, y = y, group = group, fill = emotion_label),
      colour = "white",
      linewidth = 1.05
    ) +
    geom_text(
      data = in_sector,
      aes(
        x = x, y = y, label = plot_label, angle = radial_angle,
        colour = text_colour, size = label_size
      ),
      family = label_family,
      fontface = "plain",
      hjust = 0.5,
      vjust = 0.5,
      show.legend = FALSE,
      check_overlap = FALSE
    ) +
    geom_text_repel(
      data = callouts,
      aes(x = outer_x, y = outer_y, label = plot_label, size = label_size),
      nudge_x = 0.25 * cos(callouts$angle),
      nudge_y = 0.25 * sin(callouts$angle),
      family = label_family,
      colour = style$colors[["text.primary"]],
      hjust = 0.5,
      vjust = 0.5,
      direction = "both",
      box.padding = 0.32,
      point.padding = 0.05,
      force = 2.2,
      max.overlaps = Inf,
      max.time = 8,
      min.segment.length = 0,
      segment.colour = style$colors[["text.secondary"]],
      segment.size = 0.35,
      arrow = grid::arrow(length = grid::unit(1.5, "mm"), type = "closed", ends = "last"),
      seed = 20260926,
      show.legend = FALSE
    ) +
    scale_fill_manual(values = fill_values, guide = "none") +
    scale_colour_identity() +
    scale_size_identity() +
    coord_equal(xlim = c(-1.42, 1.42), ylim = c(-1.32, 1.32), expand = FALSE, clip = "off") +
    theme_void() +
    theme(
      plot.background = element_rect(fill = "white", colour = NA),
      panel.background = element_rect(fill = "white", colour = NA),
      plot.margin = margin(24, 24, 24, 24)
    )
}

chinese_plot <- make_pie_plot(pie_data, "zh")

save_plot_pair <- function(plot, stem, width = 14, height = 14) {
  png_path <- file.path(figure_dir, paste0(stem, ".png"))
  svg_path <- file.path(figure_dir, paste0(stem, ".svg"))
  ggsave(png_path, plot, width = width, height = height, units = "in", dpi = 260, bg = "white", type = "cairo")
  grDevices::svg(svg_path, width = width, height = height, bg = "white")
  print(plot)
  dev.off()
}

save_plot_pair(chinese_plot, "emotion_label_pie_ge5_zh")

write.csv(
  pie_data[c("emotion_label", "emotion_label_zh", "article_count")],
  file.path(table_dir, "emotion_label_pie_ge5.csv"),
  row.names = FALSE,
  fileEncoding = "UTF-8"
)
cat("Chinese donut written to:", figure_dir, "\n")
