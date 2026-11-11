const apiUrl = document.currentScript.dataset.apiUrl;
    const form = document.getElementById("link-form");
    const message = document.getElementById("message");
    const result = document.getElementById("result");
    const linkContainer = document.getElementById("link-container");
    const createButton = document.getElementById("create-button");
    let requestVersion = 0;

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const version = ++requestVersion;
      message.textContent = "";
      result.hidden = true;
      linkContainer.replaceChildren();
      createButton.disabled = true;

      const data = {
        name: document.getElementById("name").value,
        url: document.getElementById("url").value
      };

      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });
        if (version !== requestVersion) return;
        if (!response.ok) {
          message.textContent = "Please enter a name and a valid HTTP or HTTPS web address.";
          return;
        }

        const linkData = await response.json();
        if (version !== requestVersion) return;
        const link = document.createElement("a");
        link.href = linkData.url;
        link.textContent = linkData.name;
        linkContainer.appendChild(link);
        result.hidden = false;
      } catch (error) {
        if (version === requestVersion) {
          message.textContent = "Could not create your link. Please try again in a moment.";
        }
      } finally {
        if (version === requestVersion) createButton.disabled = false;
      }
    });

    document.getElementById("clear-button").addEventListener("click", function () {
      requestVersion++;
      form.reset();
      result.hidden = true;
      linkContainer.replaceChildren();
      message.textContent = "";
      createButton.disabled = false;
      document.getElementById("name").focus();
    });

    document.getElementById("copy-button").addEventListener("click", async function () {
      const link = linkContainer.querySelector("a");
      if (!link) return;

      try {
        if (navigator.clipboard && navigator.clipboard.write && window.ClipboardItem) {
          const item = new ClipboardItem({
            "text/html": new Blob([link.outerHTML], { type: "text/html" }),
            "text/plain": new Blob([link.href], { type: "text/plain" })
          });
          await navigator.clipboard.write([item]);
          message.textContent = "Hyperlink copied. Paste it into a rich-text editor.";
        } else if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(link.href);
          message.textContent = "Link address copied. Your browser does not support copying formatted links.";
        } else {
          message.textContent = "Clipboard access is unavailable. Right-click the link and copy its address.";
        }
      } catch (error) {
        message.textContent = "Could not copy automatically. Right-click the link and copy its address.";
      }
    });
