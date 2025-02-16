/**
 * MayCima Module for Sora
 * 
 * This module implements the following functions:
 * - searchResults(keyword): Fetches and parses search results.
 * - extractDetails(url): Fetches a details page and extracts description, aliases, and airdate.
 * - extractEpisodes(url): Fetches the page and extracts episode links and numbers.
 * - extractStreamUrl(url): Fetches the page and extracts the stream URL.
 *
 * Note: This implementation assumes that MayCima’s HTML structure contains:
 *   - Search results inside elements with class "movie-item", where:
 *       - The link is in an <a> tag (href attribute),
 *       - The title is inside an <h3> tag,
 *       - The image is in an <img> tag.
 *   - Details within:
 *       - A <div class="movie-description"> for the description,
 *       - A <span class="alias"> for alternate titles,
 *       - A <span class="airdate"> for the release date.
 *   - Episodes as <a> elements with class "episode-link" that include the word "Episode" followed by a number.
 *   - The stream URL embedded in a <source> tag with a .m3u8 URL.
 *
 * Adjust the regular expressions as needed.
 */

async function searchResults(keyword) {
  try {
    const encodedKeyword = encodeURIComponent(keyword);
    const searchUrl = `https://maycima.com/search/${encodedKeyword}`;
    // For iOS testing, assign response directly instead of using .text()
    const html = await fetch(searchUrl);
    
    const results = [];
    // Assume each result is wrapped in a div with class "movie-item"
    const itemRegex = /<div class="movie-item">([\s\S]*?)<\/div>/g;
    let match;
    while ((match = itemRegex.exec(html)) !== null) {
      const itemHtml = match[1];
      const hrefMatch = itemHtml.match(/<a\s+href="([^"]+)"/);
      const titleMatch = itemHtml.match(/<h3>([^<]+)<\/h3>/);
      const imgMatch = itemHtml.match(/<img[^>]+src="([^"]+)"/);
      
      if (hrefMatch && titleMatch) {
        let href = hrefMatch[1].trim();
        // Ensure absolute URL
        if (!href.startsWith("http")) {
          href = "https://maycima.com" + href;
        }
        results.push({
          title: titleMatch[1].trim(),
          image: imgMatch ? imgMatch[1].trim() : "",
          href: href
        });
      }
    }
    return JSON.stringify(results);
  } catch (error) {
    console.error("Search error:", error);
    return JSON.stringify([{ title: 'Error', image: '', href: '' }]);
  }
}

async function extractDetails(url) {
  try {
    const html = await fetch(url);
    
    // Extract description
    const descriptionMatch = html.match(/<div class="movie-description">([\s\S]*?)<\/div>/);
    const description = descriptionMatch ? descriptionMatch[1].trim() : 'No description available';
    
    // Extract aliases (alternative title)
    const aliasesMatch = html.match(/<span class="alias">([^<]+)<\/span>/);
    const aliases = aliasesMatch ? aliasesMatch[1].trim() : 'N/A';
    
    // Extract airdate
    const airdateMatch = html.match(/<span class="airdate">([^<]+)<\/span>/);
    const airdate = airdateMatch ? airdateMatch[1].trim() : 'Unknown';
    
    return JSON.stringify([{
      description: description,
      aliases: aliases,
      airdate: airdate
    }]);
  } catch (error) {
    console.error("Details error:", error);
    return JSON.stringify([{
      description: 'Error loading description',
      aliases: 'N/A',
      airdate: 'Unknown'
    }]);
  }
}

async function extractEpisodes(url) {
  try {
    const html = await fetch(url);
    const episodes = [];
    // Assume episodes are in links with class "episode-link" containing "Episode" and a number.
    const episodeRegex = /<a[^>]+class="episode-link"[^>]+href="([^"]+)"[^>]*>[\s\S]*?Episode\s+(\d+)[\s\S]*?<\/a>/gi;
    let match;
    while ((match = episodeRegex.exec(html)) !== null) {
      let href = match[1].trim();
      const number = match[2].trim();
      if (!href.startsWith("http")) {
        href = "https://maycima.com" + href;
      }
      episodes.push({
        href: href,
        number: number
      });
    }
    // Fallback: if no episodes found, assume a single episode
    if (episodes.length === 0) {
      episodes.push({
        href: url,
        number: "1"
      });
    }
    return JSON.stringify(episodes);
  } catch (error) {
    console.error("Episodes error:", error);
    return JSON.stringify([]);
  }
}

async function extractStreamUrl(url) {
  try {
    const html = await fetch(url);
    // Look for a <source> tag with a .m3u8 URL
    const streamMatch = html.match(/<source[^>]+src="([^"]+\.m3u8[^"]*)"/);
    return streamMatch ? streamMatch[1] : null;
  } catch (error) {
    console.error("Stream URL error:", error);
    return null;
  }
}

// Export functions if needed (for Node.js testing)
// module.exports = { searchResults, extractDetails, extractEpisodes, extractStreamUrl };
