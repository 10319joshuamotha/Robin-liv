const api = globalThis.browser || globalThis.chrome;
const CLIENT = Math.random().toString(36).slice(2);
const BASE = "http://127.0.0.1:8765";

async function post(path, body) {
  try {
    await fetch(BASE + path, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  } catch (_) {}
}

async function syncTabs() {
  try {
    const tabs = await api.tabs.query({});
    const normal = tabs.filter(t => !t.incognito).map(t => ({
      id:t.id, windowId:t.windowId, client:CLIENT, browser: navigator.userAgent.includes("Edg/") ? "edge" : "chromium",
      title:t.title || "", url:t.url || "", active:!!t.active, incognito:false
    }));
    await post("/tabs", {client:CLIENT, tabs:normal});
  } catch (_) {}
}

async function poll() {
  try {
    const r = await fetch(BASE + "/poll?client=" + encodeURIComponent(CLIENT));
    const cmd = await r.json();
    if (!cmd || !cmd.action) return;
    if (cmd.action === "inspect") {
      try {
        const t = await api.tabs.get(cmd.tabId);
        if (!t || t.incognito) throw new Error("tab is incognito or unavailable");
        const res = await api.scripting.executeScript({
          target:{tabId:cmd.tabId},
          func:()=>({text:document.body ? document.body.innerText : "", title:document.title, url:location.href})
        });
        const v = res && res[0] && res[0].result ? res[0].result : {};
        await post("/result", {id:cmd.id, text:(v.text||"").slice(0,12000), title:v.title||"", url:v.url||""});
      } catch (e) {
        await post("/result", {id:cmd.id, error:String(e)});
      }
    }
  } catch (_) {}
}

syncTabs();
setInterval(syncTabs, 1500);
setInterval(poll, 400);
api.tabs.onCreated?.addListener(syncTabs);
api.tabs.onRemoved?.addListener(syncTabs);
api.tabs.onUpdated?.addListener(syncTabs);
api.windows?.onCreated?.addListener(syncTabs);
api.windows?.onRemoved?.addListener(syncTabs);
