import fitz  # PyMuPDF
import base64
from io import BytesIO

def extract_text_from_region(pdf_path, page_number, x1, y1, x2, y2):
    doc = fitz.open(pdf_path)
    page = doc.load_page(page_number)
    rect = fitz.Rect(x1, y1, x2, y2)
    text = page.get_text("text", clip=rect)
    doc.close()
    return text.strip()

def extract_content_from_region(pdf_path, page_number, x1, y1, x2, y2):
    """Extract both text and images from a PDF region."""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        rect = fitz.Rect(x1, y1, x2, y2)
        
        # Extract text
        text = page.get_text("text", clip=rect).strip()
        
        # Extract images with error handling
        images = []
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Get image position - this can fail for some images
                    try:
                        img_rect = page.get_image_bbox(img)
                        
                        # Check if image intersects with selection rectangle
                        if img_rect.intersects(rect):
                            # Convert to base64
                            base64_image = base64.b64encode(image_bytes).decode('utf-8')
                            images.append({
                                "data": base64_image,
                                "ext": image_ext,
                                "index": img_index
                            })
                    except Exception as bbox_error:
                        # Skip this image if we can't get its bounding box
                        print(f"Warning: Could not get bounding box for image {img_index}: {bbox_error}")
                        continue
                        
                except Exception as img_error:
                    # Skip this image if extraction fails
                    print(f"Warning: Could not extract image {img_index}: {img_error}")
                    continue
                    
        except Exception as image_list_error:
            print(f"Warning: Could not get image list: {image_list_error}")
            # Continue without images
        
        doc.close()
        
        return {
            "text": text,
            "images": images,
            "has_images": len(images) > 0
        }
        
    except Exception as e:
        print(f"Error in extract_content_from_region: {e}")
        # Return minimal response on error
        return {
            "text": "",
            "images": [],
            "has_images": False
        }
