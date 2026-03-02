import { useState } from "react";
import { pdfjs } from 'react-pdf';
import PDFViewer from "./components/PDFViewer";
import { uploadPDF, extractContent, saveMarkdown } from "./services/api";

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString();

export default function App() {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState("");
  const [selectedText, setSelectedText] = useState("");
  const [markdownContent, setMarkdownContent] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [shareUrl, setShareUrl] = useState("");
  const [savingLink, setSavingLink] = useState(false);

  const handleUpload = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    
    setError("");
    setLoading(true);
    
    try {
      const res = await uploadPDF(f);
      setPdfUrl(res.pdf_url);
      setFile(f);
    } catch (err) {
      console.error("Upload error:", err);
      setError(`Failed to upload PDF: ${err.response?.data?.detail || err.message || "Unknown error"}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = async (region) => {
    if (!file) return;
    
    setError("");
    
    try {
      const data = {
        filename: file.name,
        page_number: region.page,
        x1: region.x1,
        y1: region.y1,
        x2: region.x2,
        y2: region.y2,
      };
      const res = await extractContent(data);
      
      // Check if the response contains an error
      if (res.error) {
        setError(res.error);
        return;
      }
      
      setSelectedText(res.text);
      
      // Add to markdown content (includes embedded images)
      if (res.markdown && res.markdown.trim()) {
        setMarkdownContent(prev => {
          const newContent = prev ? `${prev}\n\n${res.markdown}` : res.markdown;
          // Reset share URL when content changes
          setShareUrl("");
          return newContent;
        });
        
        // Show info if images were found
        if (res.has_images) {
          console.log(`✅ Extracted ${res.image_count} image(s) from selection`);
        }
      }
    } catch (err) {
      console.error("Extract error:", err);
      setError(`Failed to extract content: ${err.response?.data?.detail || err.message || "Unknown error"}`);
    }
  };

  const downloadMarkdown = () => {
    if (!markdownContent) return;
    
    const blob = new Blob([markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${file?.name.replace('.pdf', '') || 'extracted'}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearMarkdown = () => {
    setMarkdownContent("");
    setSelectedText("");
    setShareUrl("");
  };

  const handleSaveLink = async () => {
    if (!markdownContent.trim()) return;

    setError("");
    setSavingLink(true);

    try {
      const title =
        file?.name?.toLowerCase().endsWith(".pdf")
          ? file.name.slice(0, -4)
          : file?.name || "Extracted content";

      const res = await saveMarkdown({
        title,
        content: markdownContent,
      });

      if (res.error) {
        setError(res.error);
        return;
      }

      setShareUrl(res.url);
    } catch (err) {
      console.error("Save link error:", err);
      setError(
        `Failed to create shareable link: ${
          err.response?.data?.detail || err.message || "Unknown error"
        }`
      );
    } finally {
      setSavingLink(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 1200, margin: '0 auto' }}>
      <h1>PDF → Markdown Tool</h1>
      <p style={{ color: '#666' }}>Upload a PDF, navigate pages, and drag to select text regions</p>
      
      <input type="file" accept="application/pdf" onChange={handleUpload} disabled={loading} />
      {loading && <p style={{ color: "blue" }}>Uploading...</p>}
      {error && <p style={{ color: "red", fontWeight: "bold" }}>{error}</p>}
      
      {pdfUrl && <PDFViewer fileUrl={pdfUrl} onSelect={handleSelect} />}
      
      {markdownContent && (
        <div style={{ marginTop: 30, position: 'relative', zIndex: 5 }}>
          <div style={{ display: 'flex', gap: 10, marginBottom: 10, position: 'relative', zIndex: 10 }}>
            <h3>Extracted Markdown Content</h3>
            <button 
              onClick={downloadMarkdown}
              style={{ 
                padding: '8px 16px', 
                background: '#4CAF50', 
                color: 'white', 
                border: 'none', 
                borderRadius: 4,
                cursor: 'pointer',
                position: 'relative',
                zIndex: 10
              }}
            >
              📥 Download .md
            </button>
            <button 
              onClick={clearMarkdown}
              style={{ 
                padding: '8px 16px', 
                background: '#f44336', 
                color: 'white', 
                border: 'none', 
                borderRadius: 4,
                cursor: 'pointer',
                position: 'relative',
                zIndex: 10
              }}
            >
              🗑️ Clear
            </button>
            <button
              onClick={handleSaveLink}
              disabled={savingLink}
              style={{
                padding: '8px 16px',
                background: '#2196F3',
                color: 'white',
                border: 'none',
                borderRadius: 4,
                cursor: savingLink ? 'default' : 'pointer',
                opacity: savingLink ? 0.7 : 1,
                position: 'relative',
                zIndex: 10
              }}
            >
              {savingLink ? "Saving..." : "🔗 Get shareable link"}
            </button>
          </div>
          <textarea
            style={{ 
              width: "100%", 
              height: "300px", 
              fontFamily: 'monospace',
              padding: 10,
              border: '1px solid #ccc',
              borderRadius: 4
            }}
            value={markdownContent}
            onChange={(e) => setMarkdownContent(e.target.value)}
          />
          {shareUrl && (
            <div
              style={{
                marginTop: 10,
                padding: 10,
                background: '#e3f2fd',
                borderRadius: 4,
                border: '1px solid #90caf9',
              }}
            >
              <strong>Shareable link:</strong>{" "}
              <a href={shareUrl} target="_blank" rel="noreferrer">
                {shareUrl}
              </a>
            </div>
          )}
          {selectedText && (
            <div style={{ marginTop: 10, padding: 10, background: '#f0f0f0', borderRadius: 4 }}>
              <strong>Last selection:</strong>
              <pre style={{ margin: '5px 0', whiteSpace: 'pre-wrap' }}>{selectedText}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
