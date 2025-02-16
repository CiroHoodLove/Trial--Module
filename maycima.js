/**
 * MyCima Module for Sora
 *
 * Implements:
 *   - searchResults(keyword): Searches and returns an array of items.
 *   - extractDetails(url): Extracts description, aliases, and airdate.
 *   - extractEpisodes(url): Finds episode links using "الحلقة".
 *   - extractStreamUrl(url): Extracts the direct stream URL (HLS/MP4).
 */

async function searchResults(keyword) {
  try {
    const encodedKeyword = encodeURIComponent(keyword);
    const searchUrl = `https://maycima.com/search/${encodedKeyword}`;
    const html = await fetch(searchUrl);

    const results = [];
    const itemRegex = /<div\s+class=["']PostItem["']>([\s\S]*?)<\/div>/gi;
    let match;
    while ((match = itemRegex.exec(html)) !== null) {
      const itemHtml = match[1];

      const hrefMatch = itemHtml.match(/<a\s+href=["']([^"']+)["']/i);
      const imgMatch = itemHtml.match(/<img\s+[^>]*src=["']([^"']+)["']/i);
      const titleMatch = itemHtml.match(/<(?:h2|h3)[^>]*>([^<]+)<\/(?:h2|h3)>/i);

      if (hrefMatch && titleMatch) {
        let href = hrefMatch[1].trim();
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
    return JSON.stringify([{ title: "Error", image: "", href: "" }]);
  }
}

async function extractDetails(url) {
  try {
    const html = await fetch(url);

    const descMatch = html.match(/<div\s+class=["']PostItemContent["']>([\s\S]*?)<\/div>/i);
    const description = descMatch
      ? descMatch[1].replace(/<[^>]+>/g, "").trim()
      : "No description available";

    const aliasMatch = html.match(/<span\s+class=["']alias["']>([^<]+)<\/span>/i);
    const aliases = aliasMatch ? aliasMatch[1].trim() : "N/A";

    const airdateMatch = html.match(/<span\s+class=["']airdate["']>([^<]+)<\/span>/i);
    const airdate = airdateMatch ? airdateMatch[1].trim() : "Unknown";

    return JSON.stringify([{
      description: description,
      aliases: aliases,
      airdate: airdate
    }]);
  } catch (error) {
    console.error("Details error:", error);
    return JSON.stringify([{
      description: "Error loading description",
      aliases: "N/A",
      airdate: "Unknown"
    }]);
  }
}

async function extractEpisodes(url) {
  try {
    const html = await fetch(url);
    const episodes = [];
    const episodeRegex = /<a\s+[^>]*href=["']([^"']+)["'][^>]*>(?:[\s\S]*?الحلقة\s*([\d]+)[\s\S]*?)<\/a>/gi;
    let match;
    while ((match = episodeRegex.exec(html)) !== null) {
      let href = match[1].trim();
      const number = match[2] ? match[2].trim() : "1";
      if (!href.startsWith("http")) {
        href = "https://maycima.com" + href;
      }
      episodes.push({
        href: href,
        number: number
      });
    }
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
    const streamMatch = html.match(/<source\s+[^>]*src=["']([^"']+\.(?:m3u8|mp4))["']/i);
    return streamMatch ? streamMatch[1].trim() : null;
  } catch (error) {
    console.error("Stream URL error:", error);
    return null;
  }
}

// Uncomment for Node.js testing
// module.exports = { searchResults, extractDetails, extractEpisodes, extractStreamUrl };
