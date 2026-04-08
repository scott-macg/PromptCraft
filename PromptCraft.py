import streamlit as st
import streamlit.components.v1 as components
import math

# --- Page Config & Branding ---
st.set_page_config(page_title="PromptCraft: Restoration Wizard", page_icon="🛠️")
st.title("🛠️ PromptCraft: Image Restoration Wizard")
st.markdown("Craft high-fidelity prompts for Gemini restoration and enhancement.")

# --- Backend Math & Logic ---
def calculate_pixel_dimensions(selected_dim, custom_val, unit, dpi_string, use_case, multiplier):
    """Translates physical dimensions and DPI into exact pixel coordinates and aspect ratios."""
    if selected_dim == "Scale Original (Multiplier)":
        return f"scale original resolution by {multiplier}"

    # Extract integer DPI
    try:
        dpi_val = int(dpi_string.split(" ")[0]) if use_case != "Digital Display" else 72
    except:
        dpi_val = 300

    final_w, final_h = 0, 0

    if selected_dim == "Custom" and custom_val:
        try:
            # Parse user input like "2000x1500"
            w_str, h_str = custom_val.lower().replace(" ", "").split("x")
            w, h = float(w_str), float(h_str)
            
            if unit == "inches":
                final_w, final_h = int(w * dpi_val), int(h * dpi_val)
            elif unit == "cm":
                final_w, final_h = int((w / 2.54) * dpi_val), int((h / 2.54) * dpi_val)
            else: # pixels
                final_w, final_h = int(w), int(h)
        except:
            return "" # Fallback if user types gibberish in the custom box
    else:
        # Parse predefined dropdowns like "1920x1080 (HD)" or "6x4"
        raw_dim = selected_dim.split(" ")[0] 
        try:
            w_str, h_str = raw_dim.split("x")
            w, h = float(w_str), float(h_str)
            if use_case == "Digital Display":
                final_w, final_h = int(w), int(h)
            else: # Inches
                final_w, final_h = int(w * dpi_val), int(h * dpi_val)
        except:
            return ""

    if final_w > 0 and final_h > 0:
        # Calculate Aspect Ratio
        divisor = math.gcd(final_w, final_h)
        ratio_w = int(final_w / divisor)
        ratio_h = int(final_h / divisor)
        
        # Prevent massive, unhelpful ratios (e.g., if user enters 1921x1080)
        if ratio_w > 32 or ratio_h > 32:
            return f"exact output resolution {final_w}x{final_h} pixels"
            
        return f"{ratio_w}:{ratio_h} aspect ratio, exact output resolution {final_w}x{final_h} pixels"
    
    return ""

def build_gemini_prompt(dimensions, orientation, smart_crop, aspect_mode, damage_types, reconstruct_missing, fidelity_mode, skin_texture, color_profile, vignette, extra_instructions):
    """Compiles UI inputs into a Gemini-optimized diffusion prompt."""
    
    # Base Descriptive Tags
    visual_tags = [
        "Faithful photographic restoration",
        "highly detailed",
        "photorealistic",
        "sharp focus",
        "expanded high dynamic range",
        f"{orientation.lower()} orientation"
    ]
    
    # Explicit Sizing Constraint
    if dimensions and dimensions.strip() != "":
        if "scale original" in dimensions.lower():
            visual_tags.append(dimensions.lower())
        else:
            visual_tags.append(dimensions) # The calculation function already formats the string nicely
    
    # Composition
    if smart_crop:
         visual_tags.append("perfectly framed subjects")
    if aspect_mode == "Fill (Crop to fit)":
         visual_tags.append("edge-to-edge subject framing")
         
    # Structural Repair
    if damage_types:
        visual_tags.append("flawless surface")
        visual_tags.append("pristine archival condition")
    if reconstruct_missing:
        visual_tags.append("seamless structural reconstruction")
        
    # Subject Fidelity
    clean_fidelity = fidelity_mode.split(" (")[0]
    if clean_fidelity == "Conservative":
         visual_tags.append("exact original structure")
         visual_tags.append("exact subject likeness")
         
    visual_tags.append(f"{skin_texture.lower()}")
    
    # Aesthetics & Style
    if color_profile != "Original":
         visual_tags.append(f"{color_profile.lower()} colorization")
         
    if vignette != "None":
         visual_tags.append(f"{vignette.lower()} vignette")
         
    # Compile the positive description
    gemini_prompt = ", ".join(visual_tags)
    
    # Gemini-Specific Negative Constraints
    negatives = []
    if vignette == "None":
         negatives.append("vignette")
    if clean_fidelity == "Conservative":
         negatives.append("new facial features")
         
    negatives.extend(["artifacts", "hallucinations", "destructive enhancements"])
    
    gemini_prompt += f". Strictly avoid: {', '.join(negatives)}."
    
    # User Notes
    if extra_instructions.strip():
        gemini_prompt += f" SPECIFIC FOCUS: {extra_instructions.strip()}"
        
    return gemini_prompt

# --- 1. Output Strategy ---
with st.expander("Step 1: Output Strategy", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        use_case = st.selectbox("Intended Use", ["Digital Display", "Home Printing", "Professional Printing Service"])
        orientation = st.radio("Target Orientation", ["Landscape", "Portrait"])
        
        if use_case == "Digital Display":
            default_dpi, default_unit_idx = 0, 0
        else:
            default_dpi, default_unit_idx = 1 if use_case == "Home Printing" else 2, 1
            
        dpi = st.radio("DPI Setting", ["72 (Web)", "300 (Standard Print)", "600 (High-End Print)"], index=default_dpi)
        
    with col2:
        if use_case == "Digital Display":
            if orientation == "Landscape":
                dim_options = ["1920x1080 (HD)", "2560x1440 (QHD)", "3840x2160 (4K)", "Custom"]
            else:
                dim_options = ["1080x1920 (Vertical HD)", "1440x2560 (Vertical QHD)", "2160x3840 (Vertical 4K)", "1080x1080 (Square)", "Custom"]
        else:
            if orientation == "Landscape":
                 dim_options = ["6x4", "7x5", "10x8", "11x8.5", "14x11", "20x16", "Custom"]
            else:
                 dim_options = ["4x6", "5x7", "8x10", "8.5x11", "11x14", "16x20", "Custom"]
            
        dim_options.insert(-1, "Scale Original (Multiplier)")
        selected_dim = st.selectbox("Target Dimensions", dim_options)
        
        if selected_dim == "Custom":
            subcol1, subcol2 = st.columns([2, 1])
            with subcol1:
                custom_val = st.text_input("Size (WxH):", placeholder="e.g., 2000x1500")
            with subcol2:
                unit = st.selectbox("Unit:", ["px", "inches", "cm"], index=default_unit_idx)
            dimensions = f"{custom_val}{unit}" if custom_val else ""
        elif selected_dim == "Scale Original (Multiplier)":
            multiplier = st.selectbox("Select Scale Multiplier:", ["1.5x", "2.0x", "2.5x", "3.0x", "3.5x", "4.0x"])
            dimensions = f"Scale original size by {multiplier}"
        else: