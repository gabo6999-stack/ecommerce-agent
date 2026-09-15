/* Catálogo compartido por las tres variantes: mismos datos, distinta puesta
   en escena. Sale de rediseno/index.html, que es la fuente original.
   Los precios y los lotes son de ejemplo: no hay conexión a WooCommerce. */
const PYS_CATEGORIAS = {
  "glp1":"GLP-1",
  "rep":"Reparación",
  "lon":"Longevidad",
  "gh":"Secretagogos",
  "noo":"Nootrópicos",
  "acc":"Accesorios",
  "sup":"Suplementos"
};

const PYS_CATALOGO = [
 { cat:"glp1", nombre:"Retatrutida", sub:"Triple agonista GLP-1 / GIP / glucagón.",
   dosis:"30 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:4900, img:"img/vial-retatrutida-30-mg.jpg" },
 { cat:"glp1", nombre:"Tirzepatida 30 mg", sub:"Doble agonista incretínico GLP-1 / GIP.",
   dosis:"30 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:3600, img:"img/vial-tirzepatida-30-mg.jpg" },
 { cat:"glp1", nombre:"Tirzepatida 60 mg", sub:"Presentación multidosis del doble agonista.",
   dosis:"60 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:6400, img:"img/vial-tirzepatida-60-mg.jpg" },
 { cat:"glp1", nombre:"Semaglutida 20 mg", sub:"Agonista GLP-1, presentación multidosis.",
   dosis:"20 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:3200, img:"img/vial-semaglutida-20-mg.jpg" },
 { cat:"glp1", nombre:"Semaglutida 5 mg", sub:"Agonista GLP-1.",
   dosis:"5 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1450, img:"img/vial-semaglutida-5-mg.jpg" },
 { cat:"rep", nombre:"BPC-157 + TB500", sub:"Mezcla para reparación de tejido. Ficha con 7 referencias verificadas en PubMed.",
   dosis:"5/5 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:2150, img:"img/vial-bpc-157-tb500-5-5mg.jpg" },
 { cat:"rep", nombre:"GHK-Cu", sub:"Tripéptido de cobre.",
   dosis:"100 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1780, img:"img/vial-ghk-cu-100-mg.jpg" },
 { cat:"lon", nombre:"MOTS-c 10 mg", sub:"Péptido derivado del ADN mitocondrial.",
   dosis:"10 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1890, img:"img/vial-mots-c-10-mg.jpg" },
 { cat:"lon", nombre:"MOTS-c 40 mg", sub:"Presentación multidosis del péptido mitocondrial.",
   dosis:"40 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:4950, img:"img/vial-mots-c-40-mg.jpg" },
 { cat:"lon", nombre:"NAD+", sub:"Dinucleótido para protocolos de longevidad.",
   dosis:"500 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:2400, img:"img/vial-nad-500-mg.jpg" },
 { cat:"gh", nombre:"CJC-1295 + Ipamorelin", sub:"Análogo de GHRH sin DAC más secretagogo.",
   dosis:"5/5 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1320, img:"img/vial-cjc-1295-ipamorelin-no-dac-5-5mg.jpg" },
 { cat:"gh", nombre:"Sermorelin", sub:"Análogo de GHRH 1-29.",
   dosis:"10 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1540, img:"img/vial-sermorelin-10-mg.jpg" },
 { cat:"gh", nombre:"IGF-1 LR3", sub:"Análogo de IGF-1 de vida media larga.",
   dosis:"1 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:2290, img:"img/vial-igf-1-lr3-1-mg.jpg" },
 { cat:"noo", nombre:"Selank", sub:"Heptapéptido nootrópico.",
   dosis:"10 mg", forma:"liofilizado", pureza:"99 % HPLC", precio:1180, img:"img/vial-selank-10-mg.jpg" },
 { cat:"acc", nombre:"Agua bacteriostática", sub:"Alcohol bencílico 0.9 %, para reconstitución.",
   dosis:"10 ml", forma:"estéril", pureza:"USP", precio:180, img:"img/vial-agua-bacteriostatica-0-9-alcohol-bencilico.jpg" },
 { cat:"sup", nombre:"Omega-3 2500 mg", sub:"EPA/DHA concentrado, 120 softgels.",
   dosis:"120 caps", forma:"EPA 900", pureza:"DHA 600", precio:690, img:null },
 { cat:"sup", nombre:"Zinc Picolinato 50 mg", sub:"Alta biodisponibilidad, 240 cápsulas.",
   dosis:"240 caps", forma:"50 mg", pureza:"8 meses", precio:420, img:null },
 { cat:"sup", nombre:"Glutatión 1500 mg", sub:"Antioxidante intracelular y soporte de detoxificación.",
   dosis:"120 caps", forma:"1500 mg", pureza:"setria", precio:860, img:null },
];

/* el lote en curso que se enseña en la portada de las tres variantes */
const PYS_LOTE = {
  id: "PYS-2609-RT", producto: "Retatrutida 30 mg", liberado: "04 SEP 2026",
  metodo: "HPLC-UV 214 nm", pureza: 99.24, masa: 4731.3, endotoxinas: "<0.5 EU",
  tr: 8.42
};
