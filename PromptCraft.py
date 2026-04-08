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
    """Compiles UI inputs into a Gemini-optimized diffusion prompt, adjusting detail based on fidelity."""
    
    # Base Descriptive Tags
    visual_tags = [
        "Photographic restoration",
        "expanded high dynamic range",
        f"{orientation.lower()} orientation"
    ]
    
    # Explicit Sizing Constraint
    if dimensions and dimensions.strip() != "":
        if "scale original" in dimensions.lower():
            visual_tags.append(dimensions.lower())
        else:
            visual_tags.append(dimensions)
    
    # Composition (Updated for clarity)
    if smart_crop:
         visual_tags.append("tightly framed on primary subject")
    if aspect_mode == "Fill (Crop to fit)":
         visual_tags.append("cropped to fill frame")
         
    # Structural Repair
    if damage_types:
        visual_tags.append("clean surface")
        visual_tags.append("archival condition")
    if reconstruct_missing:
        visual_tags.append("seamless structural reconstruction")
        
    # Subject Fidelity & Dynamic Detail Logic
    clean_fidelity = fidelity_mode.split(" (")[0]
    negatives = []
    
    if clean_fidelity == "Conservative":
         # Prioritize original pixels over artificial sharpness
         visual_tags.extend(["exact original structure", "gentle denoise", "preserve original clarity"])
         negatives.extend(["new details", "invented elements", "hallucinations", "new facial features", "over-sharpening"])
         
    elif clean_fidelity == "Reference-Based":
         # Balance between sharpness and matching the reference face
         visual_tags.extend(["exact subject likeness matching reference", "sharp focus", "highly detailed"])
         negatives.extend(["altered identity", "unrecognizable features", "hallucinated faces"])
         
    else: # Generative
         # Take the training wheels off for maximum visual quality
         visual_tags.extend(["highly detailed", "photorealistic", "sharp focus", "plausible historical details"])
         # We deliberately DO NOT ban hallucinations here, as they are required for generative sharpness.
         
    visual_tags.append(f"{skin_texture.lower()}")
    
    # Aesthetics & Style
    if color_profile != "Original":
         visual_tags.append(f"{color_profile.lower()} colorization")
         
    if vignette != "None":
         visual_tags.append(f"{vignette.lower()} vignette")
         
    # Compile the positive description
    gemini_prompt = ", ".join(visual_tags)
    
    # Finalize Negatives
    if vignette == "None":
         negatives.append("vignette")
         
    negatives.extend(["digital artifacts", "destructive enhancements"])
    
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
            dimensions = f"{selected_dim} inches" if use_case != "Digital Display" and "inches" not in selected_dim else selected_dim

# --- 2. Composition & Aspect Ratio ---
with st.expander("Step 2: Composition & Aspect Ratio"):
    aspect_mode = st.selectbox("How should the image fit the new dimensions?", 
                               ["Fill (Crop to fit)", "Fit (Letterbox/Pillarbox)", "Stretch (Distort to fit)", "Center", "Span"])
    smart_crop = st.checkbox("Enable Smart Crop")
    if smart_crop:
        st.caption("✨ AI will intelligently adjust the composition to ensure subjects and key features are preserved within the new frame.")

# --- 3. Structural Restoration ---
with st.expander("Step 3: Structural Restoration"):
    damage_types = st.multiselect("Select damage to repair:", 
                                  ["Surface Scratches", "Deep Creases/Folds", "Water Stains/Foxing", "Torn Corners/Edges", "Dust & Specks"])
    reconstruct_missing = st.checkbox("Use bilateral symmetry to reconstruct missing sections?")

# --- 4. Subject Fidelity ---
with st.expander("Step 4: Subject Fidelity"):
    fidelity_mode = st.radio("Facial Reconstruction Mode", 
                             ["Conservative (No new features)", "Reference-Based (Use secondary photo)", "Generative (AI-assisted restoration)"])
    skin_texture = st.select_slider("Skin Texture", options=["Ultra Smooth", "Balanced", "Natural Grain"], value="Natural Grain")

# --- 5. Aesthetic & Style ---
with st.expander("Step 5: Aesthetic & Style"):
    col3, col4 = st.columns(2)
    with col3:
        color_profile = st.selectbox("Colorization", ["Original", "Natural/Realistic", "Vibrant (Kodachrome)", "Muted Documentary", "B&W", "Sepia"])
    with col4:
        vignette = st.select_slider("Vignette Strength", options=["None", "Subtle", "Heavy"])

# --- 6. Additional Instructions ---
st.markdown("### Step 6: Final Touches")
extra_instructions = st.text_area("Additional Instructions", placeholder="e.g., Make sure to keep the small birthmark on the cheek...")

# --- PROMPT GENERATION LOGIC ---
st.divider()
if st.button("Generate Restoration Prompt", type="primary"):
    
    # 1. Run the dimensional translation math on the backend
    # We use locals() checks to gracefully handle UI states where variables might not be initialized
    calculated_dimensions = calculate_pixel_dimensions(
        selected_dim, 
        custom_val if 'custom_val' in locals() else "", 
        unit if 'unit' in locals() else "px", 
        dpi, 
        use_case, 
        multiplier if 'multiplier' in locals() else "1.0x"
    )

    # 2. Call the tailored Gemini function
    master_prompt = build_gemini_prompt(
        calculated_dimensions, orientation, smart_crop, aspect_mode, damage_types, 
        reconstruct_missing, fidelity_mode, skin_texture, 
        color_profile, vignette, extra_instructions
    )
    
    st.subheader("Your Generated Gemini Prompt:")
    st.code(master_prompt, language="plaintext")
    
    # Reliable Copy Button
    copy_html = f"""
        <button onclick="copyToClipboard()" style="
            background-color: #ff4b4b; color: white; border: none; 
            padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;
        ">📋 Copy Prompt</button>
        <script>
        function copyToClipboard() {{
            const text = `{master_prompt.replace('`', '\\`').replace('$', '\\$')}`;
            navigator.clipboard.writeText(text).then(() => {{
                alert('Prompt copied to clipboard!');
            }});
        }}
        </script>
    """
    components.html(copy_html, height=50)