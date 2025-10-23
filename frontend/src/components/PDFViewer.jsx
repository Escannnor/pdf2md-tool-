import { useState, useRef, useEffect } from "react";
import { Document, Page } from "react-pdf";
import { Stage, Layer, Rect } from "react-konva";

export default function PDFViewer({ fileUrl, onSelect }) {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [selection, setSelection] = useState(null);
  const [startPos, setStartPos] = useState(null);
  const [currentPos, setCurrentPos] = useState(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [pageHeight, setPageHeight] = useState(800);
  const pageRef = useRef(null);

  const handleMouseDown = (e) => {
    const { x, y } = e.target.getStage().getPointerPosition();
    setStartPos({ x, y });
    setCurrentPos({ x, y });
    setIsDrawing(true);
    setSelection(null);
  };

  const handleMouseMove = (e) => {
    if (!isDrawing || !startPos) return;
    const { x, y } = e.target.getStage().getPointerPosition();
    setCurrentPos({ x, y });
  };

  const handleMouseUp = (e) => {
    if (!startPos) return;
    const { x, y } = e.target.getStage().getPointerPosition();
    const rect = {
      x1: Math.min(startPos.x, x),
      y1: Math.min(startPos.y, y),
      x2: Math.max(startPos.x, x),
      y2: Math.max(startPos.y, y),
    };
    setSelection(rect);
    setIsDrawing(false);
    onSelect({ ...rect, page: pageNumber - 1 }); // Pass 0-indexed page
  };

  const handleMouseLeave = () => {
    // Reset drawing state if mouse leaves canvas
    setIsDrawing(false);
  };

  const handlePageLoad = () => {
    if (pageRef.current) {
      const canvas = pageRef.current.querySelector('canvas');
      if (canvas) {
        setPageHeight(canvas.height);
      }
    }
  };

  const goToPrevPage = () => {
    setPageNumber(prev => Math.max(1, prev - 1));
    setSelection(null);
    setIsDrawing(false);
    setStartPos(null);
    setCurrentPos(null);
  };

  const goToNextPage = () => {
    setPageNumber(prev => Math.min(numPages, prev + 1));
    setSelection(null);
    setIsDrawing(false);
    setStartPos(null);
    setCurrentPos(null);
  };

  return (
    <div style={{ marginTop: 20 }}>
      <div style={{ marginBottom: 10, display: 'flex', gap: 10, alignItems: 'center' }}>
        <button onClick={goToPrevPage} disabled={pageNumber <= 1}>
          ← Previous
        </button>
        <span>
          Page {pageNumber} of {numPages}
        </span>
        <button onClick={goToNextPage} disabled={pageNumber >= numPages}>
          Next →
        </button>
      </div>

      <div style={{ position: 'relative', display: 'inline-block', userSelect: 'none' }} ref={pageRef}>
        <div style={{ pointerEvents: 'none' }}>
          <Document file={fileUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
            <Page 
              pageNumber={pageNumber} 
              width={600} 
              onLoadSuccess={handlePageLoad}
              renderTextLayer={false}
              renderAnnotationLayer={false}
            />
          </Document>
        </div>
        <Stage 
          width={600} 
          height={pageHeight}
          style={{ 
            position: 'absolute', 
            top: 0, 
            left: 0, 
            cursor: 'crosshair',
            zIndex: 1
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseLeave}
        >
          <Layer>
            {/* Show selection while drawing */}
            {isDrawing && startPos && currentPos && (
              <Rect
                x={Math.min(startPos.x, currentPos.x)}
                y={Math.min(startPos.y, currentPos.y)}
                width={Math.abs(currentPos.x - startPos.x)}
                height={Math.abs(currentPos.y - startPos.y)}
                stroke="blue"
                strokeWidth={2}
                fill="rgba(0, 0, 255, 0.1)"
                dash={[5, 5]}
              />
            )}
            {/* Show final selection */}
            {selection && !isDrawing && (
              <Rect
                x={selection.x1}
                y={selection.y1}
                width={selection.x2 - selection.x1}
                height={selection.y2 - selection.y1}
                stroke="red"
                strokeWidth={2}
                fill="rgba(255, 0, 0, 0.1)"
              />
            )}
          </Layer>
        </Stage>
      </div>
    </div>
  );
}
