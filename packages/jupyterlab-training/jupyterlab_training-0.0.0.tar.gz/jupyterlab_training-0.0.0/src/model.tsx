import { ServiceManager, Contents } from '@jupyterlab/services';
import * as jsyaml from 'js-yaml';

interface JFile {
  name: string;
  path: string;
}

interface JDirectory {
  name: string;
  type: string;
  path: string;
  metadata: any;
}

/**
 * Parse formation workspace
 */
class WorkspaceTree {
  constructor(
    public exos: JDirectory[],
    public courses: JDirectory[]
  ) {}

  private static async getArboFromMetadataFile(
    contents: Contents.IManager,
    dirPath: string,
    nbType: 'exercises' | 'courses'
  ): Promise<JDirectory[]> {
    const directory: JDirectory[] = [];
    const opts: Contents.IFetchOptions = {
      content: true
    };
    const metadataFileContent = (
      await contents.get(`${dirPath}/workspace.yml`, opts)
    ).content;
    const globalMetadata = jsyaml.safeLoad(metadataFileContent);
    for (const [name, metaData] of (Object as any).entries(globalMetadata)) {
      if (name.includes(nbType)) {
        const nbPath = `${dirPath}/${name}`;
        directory.push({
          name: name,
          type: nbType,
          path: nbPath,
          metadata: metaData
        });
      }
    }
    return directory;
  }

  public static async create(
    serviceManager: ServiceManager.IManager
  ): Promise<WorkspaceTree> {
    const { contents } = serviceManager;
    const dirPath = 'training';
    return new WorkspaceTree(
      await this.getArboFromMetadataFile(contents, dirPath, 'exercises'),
      await this.getArboFromMetadataFile(contents, dirPath, 'courses')
    );
  }
}

export { JFile, JDirectory, WorkspaceTree };
