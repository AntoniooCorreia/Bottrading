// O dashboard e uma pagina estatica que le os dados do Supabase no browser.
import fs from "node:fs";
fs.mkdirSync("public", { recursive: true });
fs.copyFileSync("web/index.html", "public/index.html");
console.log("public/index.html pronto");
