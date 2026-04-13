import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "Comfy.SILVER_ClipTextEncodeWithCache",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "SILVER_ClipTextEncodeWithCache") return;
		
		const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            origOnNodeCreated?.apply(this, arguments);
			
			const clearCacheButton = this.addWidget("button", "Clear Cache", null, () => {
				fetch("/silver_clip_text_encode_with_cache/on_clicked", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({})
				})
			});
			
        };
	
	},
});
