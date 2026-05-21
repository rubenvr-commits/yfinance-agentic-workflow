// Markdown renderer with null section filtering

export function filterEmptySections(markdown) {
  if (!markdown || typeof markdown !== 'string') {
    return '';
  }

  // Split by level-2 headers (##)
  const sections = markdown.split(/\n(?=##\s)/);
  
  const filtered = sections.filter(section => {
    // Get all lines in this section
    const lines = section.split('\n');
    
    // Find content lines (excluding headers and empty lines)
    const contentLines = lines.filter(line => {
      const trimmed = line.trim();
      // Skip headers, empty lines, and pipes (table dividers)
      return trimmed && 
             !trimmed.match(/^#{1,6}\s/) && 
             !trimmed.match(/^\|[\s\-:]+\|$/);
    });
    
    if (contentLines.length === 0) {
      return false;
    }
    
    // Check if all content is just "N/A", "null", "Información no disponible", etc
    const realContent = contentLines.filter(line => {
      const cleaned = line.toLowerCase()
        .replace(/[|:\-\s]/g, '')
        .replace(/[\[\]`*_]/g, '');
      
      const nullValues = ['na', 'null', 'nodisponible', 'informacionnodisponible', 'n/a'];
      
      return cleaned.length > 0 && !nullValues.includes(cleaned);
    });
    
    return realContent.length > 0;
  });
  
  return filtered.join('\n\n');
}

export function renderMarkdown(markdown) {
  if (!markdown || typeof markdown !== 'string') {
    return '';
  }

  // Get or create markdown-it instance
  const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true
  });
  
  // Filter empty sections first
  const cleaned = filterEmptySections(markdown);
  
  // If nothing remains after filtering, return empty string
  if (!cleaned || cleaned.trim().length === 0) {
    return '';
  }
  
  return md.render(cleaned);
}

export function renderRawMarkdown(markdown) {
  if (!markdown || typeof markdown !== 'string') {
    return '';
  }

  const md = window.markdownit({
    html: true,
    linkify: true,
    typographer: true,
    breaks: true
  });
  
  return md.render(markdown);
}
