const $=(id)=>document.getElementById(id);
const form=$("upload-form"),fileInput=$("file"),dropzone=$("dropzone"),dropzoneText=$("dropzone-text"),submitBtn=$("submit-btn");
const statusCard=$("status-card"),resultCard=$("result-card"),jobIdEl=$("job-id"),statusEl=$("status"),messageEl=$("message"),bar=$("bar"),summaryEl=$("summary"),transcriptEl=$("transcript");
const STATUS_PROGRESS={queued:10,transcribing:40,summarizing:75,done:100,error:100};
const STATUS_LABEL={queued:"เข้าคิว",transcribing:"กำลังถอดเสียง...",summarizing:"กำลังสรุป...",done:"เสร็จสิ้น ✅",error:"เกิดข้อผิดพลาด ❌"};

let currentJob = null;
let originalFileName = "meeting";

const FILE_META = {
  md:   { ext: "md",   mime: "text/markdown",                                                  desc: "Markdown" },
  docx: { ext: "docx", mime: "application/vnd.openxmlformats-officedocument.wordprocessingml.document", desc: "Word Document" },
  txt:  { ext: "txt",  mime: "text/plain",                                                     desc: "Text" },
};

["dragenter","dragover"].forEach(ev=>dropzone.addEventListener(ev,e=>{e.preventDefault();dropzone.classList.add("drag")}));
["dragleave","drop"].forEach(ev=>dropzone.addEventListener(ev,e=>{e.preventDefault();dropzone.classList.remove("drag")}));
dropzone.addEventListener("drop",e=>{if(e.dataTransfer.files.length){fileInput.files=e.dataTransfer.files;updateDropzoneLabel()}});
fileInput.addEventListener("change",updateDropzoneLabel);
function updateDropzoneLabel(){if(fileInput.files[0]){const f=fileInput.files[0];dropzoneText.innerHTML=`📎 <strong>${f.name}</strong><br/><small>${(f.size/1024/1024).toFixed(2)} MB</small>`}}

form.addEventListener("submit",async(e)=>{
  e.preventDefault();
  if(!fileInput.files[0]){alert("กรุณาเลือกไฟล์เสียง");return}
  originalFileName = fileInput.files[0].name.replace(/\.[^.]+$/, "") || "meeting";
  const fd=new FormData();fd.append("file",fileInput.files[0]);fd.append("language",$("language").value);
  submitBtn.disabled=true;resultCard.classList.add("hidden");statusCard.classList.remove("hidden");
  statusEl.textContent="กำลังอัปโหลด...";messageEl.textContent="";bar.style.width="5%";
  try{
    const res=await fetch("/api/jobs",{method:"POST",body:fd});
    if(!res.ok)throw new Error((await res.json()).detail||res.statusText);
    const{job_id}=await res.json();jobIdEl.textContent=job_id;pollJob(job_id);
  }catch(err){statusEl.innerHTML=`<span class="error">${err.message}</span>`;submitBtn.disabled=false}
});

async function pollJob(jobId){
  while(true){
    await new Promise(r=>setTimeout(r,1500));
    const res=await fetch(`/api/jobs/${jobId}`);
    if(!res.ok){statusEl.textContent="โหลดสถานะไม่สำเร็จ";break}
    const job=await res.json();
    statusEl.textContent=STATUS_LABEL[job.status]||job.status;
    messageEl.textContent=job.message||"";
    bar.style.width=(STATUS_PROGRESS[job.status]||0)+"%";
    if(job.status==="done"){
      currentJob = job;
      resultCard.classList.remove("hidden");
      summaryEl.textContent=job.summary;transcriptEl.textContent=job.transcript;
      // bind Save buttons
      bindSaveButton("dl-md",   "md");
      bindSaveButton("dl-docx", "docx");
      bindSaveButton("dl-txt",  "txt");
      submitBtn.disabled=false;break;
    }
    if(job.status==="error"){submitBtn.disabled=false;break}
  }
}

function bindSaveButton(btnId, kind){
  const el = $(btnId);
  if(!el) return;
  el.onclick = async (e) => {
    e.preventDefault();
    if(!currentJob) return;
    const url = currentJob.downloads[kind];
    if(!url){alert("ยังไม่มีไฟล์");return}
    const meta = FILE_META[kind];
    const suggestedName = `${originalFileName}-summary.${meta.ext}`;
    try {
      // โหลดไฟล์มาเป็น blob
      el.classList.add("loading");
      const resp = await fetch(url);
      if(!resp.ok) throw new Error("โหลดไฟล์ไม่สำเร็จ");
      const blob = await resp.blob();

      // ใช้ File System Access API ถ้าเบราว์เซอร์รองรับ (Chrome/Edge)
      if (window.showSaveFilePicker) {
        try {
          const handle = await window.showSaveFilePicker({
            suggestedName,
            types: [{
              description: meta.desc,
              accept: { [meta.mime]: [`.${meta.ext}`] }
            }]
          });
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
          flashMessage(`✅ บันทึกเป็น ${handle.name} แล้ว`);
        } catch (err) {
          if (err.name !== "AbortError") {
            // ผู้ใช้ไม่ได้กดยกเลิก → fallback
            fallbackDownload(blob, suggestedName);
          }
        }
      } else {
        // Fallback สำหรับ Firefox/Safari (ไม่มี picker → ใช้ default download folder)
        fallbackDownload(blob, suggestedName);
      }
    } catch (err) {
      alert("เกิดข้อผิดพลาด: " + err.message);
    } finally {
      el.classList.remove("loading");
    }
  };
}

function fallbackDownload(blob, filename){
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 100);
  flashMessage(`💾 ดาวน์โหลด ${filename} (Firefox/Safari ใช้โฟลเดอร์ Downloads เริ่มต้น)`);
}

function flashMessage(text){
  let n = $("flash");
  if(!n){
    n = document.createElement("div");
    n.id = "flash";
    n.style.cssText = "position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#22c55e;color:#052e16;padding:12px 20px;border-radius:8px;font-weight:600;z-index:1000;box-shadow:0 4px 16px rgba(0,0,0,.3);transition:opacity .3s";
    document.body.appendChild(n);
  }
  n.textContent = text;
  n.style.opacity = "1";
  clearTimeout(n._t);
  n._t = setTimeout(()=>{ n.style.opacity = "0"; }, 3000);
}
