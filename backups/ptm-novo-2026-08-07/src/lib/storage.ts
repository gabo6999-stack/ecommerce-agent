import { S3Client, PutObjectCommand, GetObjectCommand } from "@aws-sdk/client-s3";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
import { randomUUID } from "crypto";

// Almacenamiento de documentos del médico en Cloudflare R2 (API S3-compatible).
// Bucket PRIVADO: los archivos solo se acceden vía URL firmada temporal generada
// del lado servidor para el admin. Inicialización perezosa para no romper el build
// si faltan las variables de entorno.

type R2Config = {
  accountId: string;
  accessKeyId: string;
  secretAccessKey: string;
  bucket: string;
};

function getConfig(): R2Config | null {
  const accountId = process.env.R2_ACCOUNT_ID;
  const accessKeyId = process.env.R2_ACCESS_KEY_ID;
  const secretAccessKey = process.env.R2_SECRET_ACCESS_KEY;
  const bucket = process.env.R2_BUCKET;
  if (!accountId || !accessKeyId || !secretAccessKey || !bucket) return null;
  return { accountId, accessKeyId, secretAccessKey, bucket };
}

export function isStorageConfigured(): boolean {
  return getConfig() !== null;
}

let client: S3Client | null = null;
function getClient(cfg: R2Config): S3Client {
  if (!client) {
    client = new S3Client({
      region: "auto",
      endpoint: `https://${cfg.accountId}.r2.cloudflarestorage.com`,
      credentials: { accessKeyId: cfg.accessKeyId, secretAccessKey: cfg.secretAccessKey },
    });
  }
  return client;
}

export async function storeDoctorDocument(params: {
  doctorId: string;
  type: string;
  file: File;
}): Promise<{ fileKey: string; originalName: string }> {
  const { doctorId, type, file } = params;
  const safeName = file.name.replace(/[^\w.\-]+/g, "_");
  const cfg = getConfig();

  // Sin storage configurado: placeholder (no persiste bytes). Permite seguir
  // probando el flujo sin R2.
  if (!cfg) {
    return { fileKey: `placeholder/${doctorId}/${type}/${safeName}`, originalName: file.name };
  }

  const key = `doctors/${doctorId}/${type}/${randomUUID()}-${safeName}`;
  const bytes = Buffer.from(await file.arrayBuffer());
  await getClient(cfg).send(
    new PutObjectCommand({
      Bucket: cfg.bucket,
      Key: key,
      Body: bytes,
      ContentType: file.type || "application/octet-stream",
    })
  );
  return { fileKey: key, originalName: file.name };
}

export async function getDocumentUrl(fileKey: string): Promise<string | null> {
  const cfg = getConfig();
  // Sin storage o documento placeholder (cargado antes de configurar R2): sin vista.
  if (!cfg || fileKey.startsWith("placeholder/")) return null;
  const cmd = new GetObjectCommand({ Bucket: cfg.bucket, Key: fileKey });
  // URL firmada válida 5 minutos, solo para la revisión del admin.
  return getSignedUrl(getClient(cfg), cmd, { expiresIn: 300 });
}
