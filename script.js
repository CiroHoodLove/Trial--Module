// Helper function to clean titles
function cleanTitle(title) {
    return title
        .replace(/&#8217;/g, "'")
        .replace(/&#8211;/g, "-")
        .replace(/&#[0-9]+;/g, "")
        .trim();
}

// Search results from HTML (e.g., https://www.faselhds.care/?s=query)
function searchResults(html) {
    const results = [];
    const baseUrl = "https://www.faselhds.care/";

    // Match search result items (movies and series)
    const itemRegex = /<div class="result-item"[\s\S]*?<div class="poster">[\s\S]*?<\/div>\s*<\/div>/g;
    const items = html.match(itemRegex) || [];

    items.forEach(itemHtml => {
        // Extract title and href
        const titleMatch = itemHtml.match(/<a href="([^"]+)" title="([^"]+)">/);
        const href = titleMatch ? titleMatch[1] : "";
        let title = titleMatch ? titleMatch[2] : "";

        // Extract image
        const imgMatch = itemHtml.match(/<img src="([^"]+)" alt="[^"]*" \/>/);
        const imageUrl = imgMatch ? imgMatch[1] : "";

        if (title && href) {
            title = cleanTitle(title);
            results.push({
                title: title,
                image: imageUrl,
                href: href.startsWith("http") ? href : baseUrl + href
            });
        }
    });

    return results;
}

// Extract details from a movie/series page (e.g., https://www.faselhds.care/seasons/breaking-bad-all-seasons)
function extractDetails(html) {
    const details = [];

    // Extract description
    const descMatch = html.match(/<div class="entry-content">[\s\S]*?<p>([\s\S]*?)<\/p>/);
    let description = descMatch ? descMatch[1].trim() : "No description available";

    // Extract aliases (e.g., original title or additional info)
    const aliasesMatch = html.match(/<h1 class="entry-title"[^>]*>([^<]+)<\/h1>/);
    let aliases = aliasesMatch ? cleanTitle(aliasesMatch[1]) : "N/A";

    // Extract airdate or release year (if available)
    const airdateMatch = html.match(/<span class="year">(\d{4})<\/span>/);
    let airdate = airdateMatch ? airdateMatch[1] : "Unknown";

    if (description) {
        details.push({
            description: description,
            aliases: aliases,
            airdate: airdate
        });
    }

    return details;
}

// Extract episodes from a season/series page (e.g., https://www.faselhds.care/series/مسلسل-breaking-bad-الموسم-الأول)
function extractEpisodes(html) {
    const episodes = [];
    const baseUrl = "https://www.faselhds.care/";

    // Match episode links
    const episodeRegex = /<li class="episode">[\s\S]*?<a href="([^"]+)"[^>]*>(الحلقة \d+)<\/a>/g;
    let matches;
    while ((matches = episodeRegex.exec(html)) !== null) {
        const href = matches[1];
        const numberMatch = matches[2].match(/\d+/);
        const number = numberMatch ? numberMatch[0] : "";

        if (href && number) {
            episodes.push({
                href: href.startsWith("http") ? href : baseUrl + href,
                number: number
            });
        }
    }

    // Reverse to match typical episode order if needed
    return episodes.reverse();
}

// Extract stream URL from an episode page (e.g., https://www.faselhds.care/?p=3091)
function extractStreamUrl(html) {
    // Look for streaming sources
    const sourceRegex = /data-server="[^"]*" data-quality="([^"]+)" data-source="([^"]+)"/g;
    let match;
    let bestStream = null;

    while ((match = sourceRegex.exec(html)) !== null) {
        const quality = match[1];
        const streamUrl = match[2].replace(/&amp;/g, "&");

        // Prioritize highest quality (e.g., FHD or 1080p)
        if (quality === "FHD" || quality === "1080p") {
            bestStream = streamUrl;
            break;
        } else if (!bestStream) {
            bestStream = streamUrl; // Fallback to first available
        }
    }

    return bestStream || null;
}

// Test the script (for Node.js debugging)
const testHtml = `<div class="result-item">...</div>`; // Replace with actual HTML for testing
console.log("Search Results:", searchResults(testHtml));
