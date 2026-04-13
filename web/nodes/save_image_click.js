import { app } from "../../../scripts/app.js";

app.registerExtension({
    name: "Comfy.SILVER_SaveIMGWithClick",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== "SILVER_SaveIMGWithClick") return;
		
		let saving = false;
		
		const origOnExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			origOnExecuted?.apply(this, arguments);
			
			const status = Array.isArray(message?.silver_status)
				? message.silver_status.join("")
				: message?.silver_status;
			
			if (status === "new") {
				const btn = this._silver_save_button;
				if (btn) {
					btn.label = "Save Image";
					this.setDirtyCanvas(true, true);
				}
			}
		};
		
		const origOnNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function() {
            origOnNodeCreated?.apply(this, arguments);
			
			const saveButton = this.addWidget("button", "Save Image", null, () => {
				if (!saving) {
					saving = true;
					fetch("/silver_save_img_with_click/on_clicked", {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({ id: this.id.toString() })
					})
					.then(res => res.json())
					.then(data => {
						if (data.status === "success" || data.status === "already_saved") {
							saveButton.label = "✅ Saved";
						} else {
							saveButton.label = "❌ Failed";
						}
						this.setDirtyCanvas(true, true);
					});
					saving = false;
				}
			});
			
			this._silver_save_button = saveButton;
			
			const filename_prefix_widget = this.widgets?.find(w => w.name === "filename_prefix");
			if (filename_prefix_widget) {
                const filename_prefix_original_callback = filename_prefix_widget.callback;
                filename_prefix_widget.callback = async function(value) {
                    fetch("/silver_save_img_with_click/update_prefix", {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({ id: this.node.id.toString(), filename_prefix: value })
					});
                    if (filename_prefix_original_callback) filename_prefix_original_callback(value);
                };
            }
			
			const save_metadata_widget = this.widgets?.find(w => w.name === "save_metadata");
			if (save_metadata_widget) {
                const save_metadata_original_callback = save_metadata_widget.callback;
                save_metadata_widget.callback = async function(value) {
                    fetch("/silver_save_img_with_click/update_save_metadata", {
						method: "POST",
						headers: {
							"Content-Type": "application/json",
						},
						body: JSON.stringify({ id: this.node.id.toString(), save_metadata: value })
					});
                    if (save_metadata_original_callback) save_metadata_original_callback(value);
                };
            }
			
        };
	
	},
});
