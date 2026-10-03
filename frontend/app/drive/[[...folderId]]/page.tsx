import { DriveView } from '@/components/drive/DriveView';

export default async function DrivePage(props: { params: Promise<{ folderId?: string[] }> }) {
  const params = await props.params;
  const folderId = params.folderId ? params.folderId[0] : null;

  return (
    <div className="h-full flex flex-col">
      <DriveView currentFolderId={folderId} />
    </div>
  );
}
