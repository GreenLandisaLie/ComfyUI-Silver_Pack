# ComfyUI-Silver_Pack

Misc collection of nodes. Some are just slightly improved versions of the native ones.

## Current node list:
- [Silver] Save Image with Click -> Hybrid of native Preview and Save Image nodes. Includes a button and image(s) will only be saved when pressed.
- [Silver] CLIP Text Encode (Prompt) -> Same as the native 'CLIP Text Encode (Prompt)' node but with negative prompt widget and cache support. Useful when shuffling between prompts often, ex: A -> B -> A -> D -> C -> B , ... Conditionals whose prompt exists in cache will skip the encoding process of the Text Encoder entirely - making this node extremely fast in prompt shuffling scenarios.


<img width="988" height="440" alt="1" src="https://github.com/user-attachments/assets/cf92d14a-e8f6-4ffc-b8fd-efc9c266459b" />

