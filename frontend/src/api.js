const API="http://127.0.0.1:5000/api";
async function request(path,options={}){
  const r=await fetch(`${API}${path}`,{headers:{"Content-Type":"application/json"},...options});
  if(!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}
export const api={
 health:()=>request("/health"),
 saveProfile:p=>request("/profile",{method:"POST",body:JSON.stringify(p)}),
 recommend:p=>request("/recommend-careers",{method:"POST",body:JSON.stringify(p)}),
 gaps:p=>request("/skill-gap",{method:"POST",body:JSON.stringify(p)}),
 roadmap:p=>request("/generate-roadmap",{method:"POST",body:JSON.stringify(p)}),
 resources:()=>request("/resources"),
 projects:()=>request("/projects"),
 feedback:p=>request("/feedback",{method:"POST",body:JSON.stringify(p)}),
 progress:p=>request("/roadmap/progress",{method:"POST",body:JSON.stringify(p)})
};
