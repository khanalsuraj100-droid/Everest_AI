
const form=document.getElementById("form"), input=document.getElementById("input");
const messages=document.getElementById("messages"), welcome=document.getElementById("welcome");

function addMessage(role, content){
  welcome.style.display="none";
  const div=document.createElement("div");
  div.className="msg "+role;
  div.textContent=content;
  messages.appendChild(div);
  messages.scrollTop=messages.scrollHeight;
}
async function loadHistory(){
  const r=await fetch("/api/history"); const data=await r.json();
  data.forEach(x=>addMessage(x.role==="user"?"user":"assistant",x.content));
}
form.addEventListener("submit",async e=>{
  e.preventDefault(); const text=input.value.trim(); if(!text)return;
  addMessage("user",text); input.value="";
  const r=await fetch("/api/message",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:text})});
  const data=await r.json(); addMessage("assistant",data.reply||"Error");
});
document.getElementById("newChat").onclick=async()=>{
  await fetch("/api/new-chat",{method:"POST"}); messages.innerHTML=""; welcome.style.display="";
};
document.querySelectorAll(".quick button").forEach(b=>b.onclick=()=>{input.value=b.textContent.replace(/^[^ ]+ /,"");input.focus()});
loadHistory();
