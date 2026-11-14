import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const source = path.resolve("output/Supply_Chain_Risk_Units_1_2_Presentation.pptx");
const final = path.resolve("output/Supply_Chain_Risk_Project_Update_2026-10-25.pptx");
const build = path.resolve(".pptx_build");
await fs.mkdir(build, {recursive:true});
await fs.mkdir(path.dirname(final), {recursive:true});
const p = await Presentation.load(source);
const addText=(slide,name,text,pos,size,color,bold=false)=>{
 const s=slide.shapes.add({geometry:"textbox",name,position:pos,fill:"none",line:{style:"solid",fill:"none",width:0}});
 s.text=text; s.text.style={fontSize:size,fontFamily:"Aptos",color,bold,verticalAlignment:"middle",wrap:true}; return s;
};
const rule=(slide,x,y,w,color)=>slide.shapes.add({geometry:"rect",position:{left:x,top:y,width:w,height:3},fill:color,line:{style:"solid",fill:"none",width:0}});
const W=960,H=540, navy="#12304A", teal="#00A6A6", ink="#183044", muted="#536B7A", pale="#EEF4F6", gold="#D99A26";
{
 const s=p.slides.add({width:W,height:H,background:{fill:"#FFFFFF"}});
 addText(s,"slide-number","13",{left:52,top:24,width:35,height:30},12,muted,true);
 addText(s,"title","Progress to date",{left:52,top:58,width:850,height:54},31,navy,true);
 rule(s,52,121,856,teal);
 addText(s,"subtitle","The project now has an integrated weekly dataset and a first modeling attempt",{left:52,top:138,width:850,height:42},18,muted);
 const left=[["DATA REVIEW","Five inputs checked: GSCPI, commodity prices, freight prices, PortWatch port activity and weather."],["DATA PREPARATION","Weekly table assembled for 2020–2023; economic and port data aggregated, with weather features joined."],["MODELING SETUP","Candidate models defined: most-frequent baseline, class-weighted logistic regression and XGBoost."]];
 const right=[["VALIDATION PLAN","Time-ordered splitting and average precision were used to account for the rare positive class."],["WHAT WE LEARNED","208 weekly observations; 9 disruption weeks (4.3%), all in 2021."],["CURRENT STATUS","Preparation is substantially complete. Model selection and performance claims remain unvalidated."]];
 let y=205;
 for(let i=0;i<3;i++){
   addText(s,"left-head-"+i,left[i][0],{left:64,top:y,width:385,height:25},14,teal,true);
   addText(s,"left-body-"+i,left[i][1],{left:64,top:y+27,width:385,height:54},15,ink);
   addText(s,"right-head-"+i,right[i][0],{left:510,top:y,width:385,height:25},14,teal,true);
   addText(s,"right-body-"+i,right[i][1],{left:510,top:y+27,width:385,height:54},15,ink);
   y+=94;
 }
 addText(s,"footer","Supply Chain Disruption Risk Prediction  |  Work completed and findings through 25 Oct 2026",{left:52,top:503,width:856,height:20},10,muted);
}
{
 const s=p.slides.add({width:W,height:H,background:{fill:"#FFFFFF"}});
 addText(s,"slide-number","14",{left:52,top:24,width:35,height:30},12,muted,true);
 addText(s,"title","Model evaluation: preliminary finding",{left:52,top:58,width:850,height:54},31,navy,true);
 rule(s,52,121,856,teal);
 addText(s,"summary","The present time split cannot tell us whether the model detects future disruptions.",{left:52,top:142,width:850,height:42},21,ink,true);
 addText(s,"count-9","9",{left:80,top:214,width:205,height:80},52,gold,true);
 addText(s,"count-9-label","positive disruption weeks",{left:80,top:292,width:205,height:40},17,muted);
 addText(s,"count-199","199",{left:365,top:214,width:220,height:80},52,teal,true);
 addText(s,"count-199-label","non-disruption weeks",{left:365,top:292,width:220,height:40},17,muted);
 addText(s,"count-total","208",{left:690,top:214,width:205,height:80},52,navy,true);
 addText(s,"count-total-label","weeks in 2020–2023",{left:690,top:292,width:205,height:40},17,muted);
 rule(s,52,356,856,pale);
 addText(s,"finding-1","All 9 positive labels occur in 2021; the final 20% test period is in 2023 and contains no positive examples.",{left:64,top:378,width:830,height:44},17,ink);
 addText(s,"finding-2","AUROC is undefined for this test set. Some cross-validation folds also lack one class, so the selected baseline and scores are not reliable model comparisons.",{left:64,top:432,width:830,height:56},17,ink);
 addText(s,"footer","Current labels depend on the GSCPI threshold; verify event weeks and dates before treating them as ground truth.",{left:52,top:503,width:856,height:20},10,muted);
}
{
 const s=p.slides.add({width:W,height:H,background:{fill:"#FFFFFF"}});
 addText(s,"slide-number","15",{left:52,top:24,width:35,height:30},12,muted,true);
 addText(s,"title","What to do next",{left:52,top:58,width:850,height:54},31,navy,true);
 rule(s,52,121,856,teal);
 addText(s,"subtitle","Resolve label and evaluation design before choosing a model",{left:52,top:138,width:850,height:38},18,muted);
 const steps=[
 ["01","Audit disruption labels","Check date coverage and compare labeled weeks with the project's documented disruption events. Fix the threshold/label rule if needed."],
 ["02","Rebuild time-aware evaluation","Keep chronology. Choose test windows and fewer/custom validation folds that contain positive and negative cases; publish counts for every split."],
 ["03","Compare simple baselines","Evaluate persistence and logistic regression first, then XGBoost. Report average precision, precision/recall, confusion matrix and positive counts."],
 ["04","Check features and leakage","Use only information available at forecast time. Fit thresholds, imputers, scaling and other transformations using training data."],
 ["05","Document and decide","Record limitations and results. Define an alert threshold with the procurement user, then decide whether more positive examples or a revised target are needed."]
 ];
 let y=197;
 for(let i=0;i<steps.length;i++){
   addText(s,"step-num-"+i,steps[i][0],{left:64,top:y,width:56,height:35},18,teal,true);
   addText(s,"step-title-"+i,steps[i][1],{left:126,top:y,width:280,height:31},16,navy,true);
   addText(s,"step-desc-"+i,steps[i][2],{left:410,top:y,width:480,height:48},14,ink);
   y+=61;
 }
 addText(s,"footer","Decision gate: do not claim predictive performance until the positive labels and chronological test are valid.",{left:52,top:503,width:856,height:20},10,muted,true);
}
const draft=path.join(build,"draft.pptx");
await (await PresentationFile.exportPptx(p)).save(draft);
await fs.copyFile(draft,final);
for (let i=12;i<15;i++){
 const slide=p.slides.items[i];
 const png=await p.export({slide,format:"png",scale:1});
 await fs.writeFile(path.join(build,"slide-"+(i+1)+".png"),new Uint8Array(await png.arrayBuffer()));
}
const montage=await p.export({format:"webp",montage:true});
await fs.writeFile(path.join(build,"montage.webp"),new Uint8Array(await montage.arrayBuffer()));
console.log(JSON.stringify({final,slides:p.slides.items.length,build}));
