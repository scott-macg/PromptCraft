import streamlit as st

# --- Page Config & Branding ---
st.set_page_config(page_title="PromptCraft: Restoration Wizard", page_icon="🛠️")
st.title("🛠️ PromptCraft: Image Restoration Wizard")
st.markdown("Craft high-fidelity prompts for Gemini restoration and enhancement.")

# --- 1. Output Strategy ---
with st.expander("Step 1: Output Strategy", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        use_case = st.selectbox("Intended Use", ["Digital Display", "Home Printing", "Professional Printing Service"])
        
        # Auto-adjust the default DPI based on the selected Use Case
        if use_case == "Digital Display":
            default_dpi = 0 # 72 DPI
            default_unit_idx = 0 # Default unit to pixels
        elif use_case == "Home Printing":
            default_dpi = 1 # 300 DPI
            default_unit_idx = 1 # Default unit to inches
        else:
            default_dpi = 2 # 600 DPI
            default_unit_idx = 1 # Default unit to inches
            
        dpi = st.radio("DPI Setting", ["72 (Web)", "300 (Standard Print)", "600 (High-End Print)"], index=default_dpi)
        
    with col2:
        # Context-aware dimension options with new Multiplier and Custom options
        if use_case == "Digital Display":
            dim_options = ["1920x1080 (HD)", "1080x1080 (Social Square)", "1080x1920 (Story)", "Scale Original (Multiplier)", "Custom"]
        elif use_case == "Home Printing":
            dim_options = ["4x6", "5x7", "8x10", "8.5x11", "Scale Original (Multiplier)", "Custom"]
        else: # Professional Printing
            dim_options = ["8x10", "11x14", "16x20", "24x36", "Scale Original (Multiplier)", "Custom"]
            
        selected_dim = st.selectbox("Target Dimensions", dim_options)
        
        # Dynamic UI based on the dimension selection
        if selected_dim == "Custom":
            # Nested columns for clean Custom UI
            subcol1, subcol2 = st.columns([2, 1])
            with subcol1:
                custom_val = st.text_input("Enter Size (WxH):", placeholder="e.g., 2000x1500")
            with subcol2:
                unit = st.selectbox("Unit:", ["px", "inches", "cm"], index=default_unit_idx)
            
            # Format the output for the prompt
            dimensions = f"{custom_val}{unit}" if custom_val else ""
            
        elif selected_dim == "Scale Original (Multiplier)":
            multiplier = st.selectbox("Select Scale Multiplier:", ["1.5x", "2.0x", "2.5x", "3.0x", "3.5x", "4.0x"])
            dimensions = f"Scale original size by {multiplier}"
            
        else:
            # Handle the preset selections (adding 'inches' text if it's a print preset)
            if use_case != "Digital Display" and "inches" not in selected_dim:
                dimensions = f"{selected_dim} inches"
            else:
                dimensions = selected_dim
                
# --- 2. Structural Restoration ---
with st.expander("Step 2: Structural Restoration"):
    damage_types = st.multiselect("Select damage to repair:", 
                                  ["Surface Scratches", "Deep Creases/Folds", "Water Stains/Foxing", "Torn Corners/Edges", "Dust & Specks"])
    reconstruct_missing = st.checkbox("Use bilateral symmetry to reconstruct missing sections?")

# --- 3. Subject Fidelity ---
with st.expander("Step 3: Subject Fidelity"):
    fidelity_mode = st.radio("Facial Reconstruction Mode", 
                             ["Conservative (No new features)", "Reference-Based (Use secondary photo)", "Generative (AI-assisted restoration)"])
    skin_texture = st.select_slider("Skin Texture", options=["Ultra Smooth", "Balanced", "Natural Grain"], value="Natural Grain")

# --- 4. Environmental Enhancement ---
with st.expander("Step 4: Environmental Enhancement"):
    env_options = st.multiselect("Enhancements:", 
                                 ["Relighting (Better subject lighting)", "Sky Replacement", "Background Clean-up", "Bokeh (Background Blur)"])
    object_removal = st.text_input("Objects to remove (leave blank if none):", placeholder="e.g., power lines, red car")

# --- 5. Aesthetic & Style ---
with st.expander("Step 5: Aesthetic & Style"):
    col3, col4 = st.columns(2)
    with col3:
        color_profile = st.selectbox("Colorization", ["Original", "Natural/Realistic", "Vibrant (Kodachrome)", "Muted Documentary", "B&W", "Sepia"])
    with col4:
        vignette = st.select_slider("Vignette Strength", options=["None", "Subtle", "Heavy"])

# --- PROMPT GENERATION LOGIC ---
st.divider()
if st.button("Generate Restoration Prompt"):
    # We will build the prompt dynamically as a list of strings
    prompt_parts = ["### RESTORATION INSTRUCTIONS"]
    
    # 1. Tech Specs (Handle empty dimension box)
    dim_text = dimensions if dimensions.strip() != "" else "[Auto-Detect Best Resolution]"
    prompt_parts.append(f"**TECHNICAL SPECS:** Upscale to {dim_text} at {dpi} for {use_case}.")
    
    # 2. Structural Repair
    p_repair = f"Digitally heal {', '.join(damage_types).lower()}." if damage_types else "Ensure no alteration to original structure."
    p_symmetry = " Use bilateral symmetry to reconstruct missing sections." if reconstruct_missing else ""
    prompt_parts.append(f"**STRUCTURAL REPAIR:** {p_repair}{p_symmetry}")
    
    # 3. Subject Fidelity (Clean up the string for the prompt)
    clean_fidelity = fidelity_mode.split(" (")[0] # Removes the parenthetical explanation from the UI
    prompt_parts.append(f"**SUBJECT FIDELITY:** Apply {clean_fidelity} restoration. Maintain {skin_texture} texture. Ensure identity strictly matches the source.")
    
    # 4. Environment (ONLY add this line if options were selected)
    env_text = f"Apply: {', '.join(env_options)}. " if env_options else ""
    removal_text = f"Remove: {object_removal}." if object_removal else ""
    p_env = (env_text + removal_text).strip()
    
    if p_env:  # If p_env is not empty, add it to the prompt
        prompt_parts.append(f"**ENVIRONMENT:** {p_env}")
        
    # 5. Aesthetics
    prompt_parts.append(f"**AESTHETICS:** Colorization: {color_profile}. Vignette: {vignette}.")
    
    # 6. Guardrails
    prompt_parts.append("**GOAL:** Non-destructive enhancement with expanded dynamic range and DSLR sharpness. Zero AI artifacts.")
    
    # Join everything together with line breaks
    master_prompt = "\n".join(prompt_parts)
    
    st.subheader("Your Generated Prompt:")
    st.code(master_prompt, language="markdown")
    st.info("Copy and paste this into Gemini along with your original photo (and reference photo if applicable).")
