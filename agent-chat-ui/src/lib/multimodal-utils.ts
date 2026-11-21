import { ContentBlock } from "@langchain/core/messages";
import { toast } from "sonner";

export async function fileToContentBlock(
  file: File,
): Promise<ContentBlock.Multimodal.Data> {
  const imageTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];
  const supportedTypes = [...imageTypes, "application/pdf"];
  if (!supportedTypes.includes(file.type)) {
    toast.error(
      `Unsupported file type: ${file.type}. Supported types are: ${supportedTypes.join(", ")}`,
    );
    throw new Error(`Unsupported file type: ${file.type}`);
  }

  const data = await fileToBase64(file);
  if (imageTypes.includes(file.type)) {
    return {
      type: "image",
      mimeType: file.type,
      data,
      metadata: { name: file.name },
    };
  }

  return {
    type: "file",
    mimeType: "application/pdf",
    data,
    metadata: { filename: file.name },
  };
}

export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      resolve(result.split(",")[1]);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

export function isBase64ContentBlock(
  block: unknown,
): block is ContentBlock.Multimodal.Data {
  if (typeof block !== "object" || block === null || !("type" in block)) {
    return false;
  }

  const candidate = block as { type?: unknown; mimeType?: unknown };
  return (
    (candidate.type === "file" || candidate.type === "image") &&
    typeof candidate.mimeType === "string" &&
    (candidate.mimeType.startsWith("image/") ||
      candidate.mimeType === "application/pdf")
  );
}
