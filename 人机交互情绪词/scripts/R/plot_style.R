read_plot_style <- function(root) {
  path <- file.path(root, "config", "plot_style.csv")
  if (!file.exists(path)) {
    stop("Missing shared plot style: ", path)
  }
  rows <- read.csv(path, stringsAsFactors = FALSE, check.names = FALSE)
  colors <- setNames(rows$color, paste(rows$role, rows$key, sep = "."))
  list(
    colors = colors,
    frequency_levels = c("under-5", "5-6", "7-9", "10-14", "15-19", "20-29", "30-plus")
  )
}

read_article_color_table <- function(root) {
  path <- file.path(root, "outputs", "tables", "emotion_label_color_map.csv")
  if (!file.exists(path)) {
    stop("Run scripts/python/analyze_emotions.py first; missing ", path)
  }
  rows <- read.csv(
    path, stringsAsFactors = FALSE, check.names = FALSE,
    fileEncoding = "UTF-8-BOM"
  )
  if (anyDuplicated(rows$emotion_label) || anyDuplicated(rows$color_order)) {
    stop("Emotion labels are not unique in ", path)
  }
  rows$color_order <- as.numeric(rows$color_order)
  rows <- rows[order(rows$color_order), , drop = FALSE]
  rows
}

read_article_color_map <- function(root) {
  rows <- read_article_color_table(root)
  stats::setNames(rows$color, rows$emotion_label)
}

project_root_from_script <- function(script_path = NULL) {
  trailing <- commandArgs(trailingOnly = TRUE)
  requested <- grep("^--project-root=", trailing, value = TRUE)
  if (length(requested)) {
    return(normalizePath(sub("^--project-root=", "", requested[[1]]), mustWork = TRUE))
  }
  if (!is.null(script_path) && nzchar(script_path)) {
    return(normalizePath(file.path(dirname(script_path), "../.."), mustWork = TRUE))
  }
  normalizePath(getwd(), mustWork = TRUE)
}
