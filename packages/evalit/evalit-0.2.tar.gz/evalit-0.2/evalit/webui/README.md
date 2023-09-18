# Webui V2

logics:

```python
# get all images
prompts_dict = {}
for checkpoint in checkpoint_list:
    for prompt in prompts:
        curr_pil_image = api.generate(prompt, negative_prompt, checkpoint, generation_config)
        prompts_dict[prompt].append((checkpoint, curr_pil_image))
# stitch images together
for prompt, images in prompts_dict.items():
    # stitch images together
    titles = [f"{checkpoint}" for checkpoint, _ in images]
    stitched_images = stitch_images(images, titles)
    # save image
    save_image(stitched_images, f"{prompt}.png")
```

