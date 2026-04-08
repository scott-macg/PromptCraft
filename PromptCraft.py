import math
import streamlit as st
import streamlit.components.v1 as components

# --- Page Config & Branding ---
st.set_page_config(page_title="PromptCraft: Restoration Wizard", page_icon="🛠️")
st.title("🛠️ PromptCraft: Image Restoration Wizard")
st.markdown("Craft high-fidelity prompts for Gemini restoration and enhancement.")

# --- Gemini Prompt Builder Logic ---
def build_gemini_prompt(orientation, smart_crop, aspect_mode, damage_types, reconstruct_missing, fidelity_mode, skin_texture, color_profile, vignette, extra_instructions):
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