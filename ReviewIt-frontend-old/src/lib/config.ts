/** Styles `/api/humanize-sentence` actually honours (anything else silently runs as "academic"). */
export const STYLES = ["academic", "business", "creative", "casual", "narrative", "technical"] as const;
export const DEFAULT_STYLE = "academic";

/** How many humanize requests are sent at once (keep in line with MAX_CONCURRENT_HUMANIZE in the backend). */
export const MAX_CONCURRENT_HUMANIZE = 1;

/** The backend cuts uploaded documents to this many words before detection. */
export const MAX_ANALYSED_WORDS = 20000;
