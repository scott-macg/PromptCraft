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