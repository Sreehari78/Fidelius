"use client";

import React, { useState, useEffect } from "react";
import { useDropzone, type DropzoneOptions } from "react-dropzone";
import {
  Upload,
  Check,
  X,
  Loader2,
  Shield,
  FolderOpen,
  Download,
} from "lucide-react";
import { useRouter } from "next/navigation";

interface HeaderControl {
  visible: boolean;
  mode: "mask" | "obfuscate" | null;
  prompt: string;
}

interface SubmitData {
  fileName: string;
  headers: {
    name: string;
    mode: "mask" | "obfuscate" | null;
    prompt: string;
  }[];
  outputPath: string;
  inputPath: string; // Added inputPath to SubmitData
}

export default function HeaderControl() {
  const [files, setFiles] = useState<
    { name: string; path: string; type: string; size: number }[]
  >([]);
  const [activeFileIndex, setActiveFileIndex] = useState<number>(-1);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [jsonOutput, setJsonOutput] = useState<string>("");
  const [backendColumns, setBackendColumns] = useState<
    Record<number, string[]>
  >({});
  const [headerControls, setHeaderControls] = useState<
    Record<number, Record<string, HeaderControl>>
  >({});
  const [submitResponse, setSubmitResponse] = useState<string | null>(null);
  const [folderPath, setFolderPath] = useState<string>("");
  const [isFolderProcessing, setIsFolderProcessing] = useState<boolean>(false);
  const [folderError, setFolderError] = useState<string | null>(null);
  const [outputPath, setOutputPath] = useState<string>("");
  const [processingQueue, setProcessingQueue] = useState<number[]>([]);
  const [outputFiles, setOutputFiles] = useState<string[]>([]);
  const router = useRouter();

  useEffect(() => {
    const processNextFileInQueue = async () => {
      if (processingQueue.length > 0 && !isUploading) {
        const fileIndex = processingQueue[0];
        setIsUploading(true);

        await processFile(files[fileIndex], fileIndex);

        setProcessingQueue((prev) => prev.slice(1));
      }
    };

    processNextFileInQueue();
  }, [processingQueue, isUploading, files]);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const startIdx = files.length;
    const newFiles = acceptedFiles.map((file) => ({
      name: file.name,
      path: file.path,
      type: file.type,
      size: file.size,
    }));

    console.log("Selected files:", newFiles);
    setFiles((prev) => [...prev, ...newFiles]);

    if (activeFileIndex === -1) {
      setActiveFileIndex(startIdx);
    }

    const newIndices = Array.from(
      { length: newFiles.length },
      (_, i) => startIdx + i
    );
    setProcessingQueue((prev) => [...prev, ...newIndices]);
  };

  const processFile = async (
    file: { name: string; path: string; type: string; size: number },
    fileIndex: number
  ) => {
    if (!file) {
      setIsUploading(false);
      return;
    }

    const fileType = file.name.split(".").pop()?.toLowerCase();
    try {
      let response: Response | null = null;
      if (fileType === "csv") {
        response = await fetch("http://localhost:5000/getcsvheader", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filePath: file.path }),
        });
      } else if (fileType === "pdf") {
        response = await fetch("http://localhost:5000/getpdfheader", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ filePath: file.path }),
        });
      } else {
        throw new Error("Unsupported file type");
      }

      if (response && !response.ok) {
        throw new Error("Network response was not ok");
      }

      const result = await response.json();
      const headers: string[] = result.headers.slice(1);

      setBackendColumns((prev) => ({ ...prev, [fileIndex]: headers }));

      const initialControls: Record<string, HeaderControl> = headers.reduce(
        (acc, col) => {
          acc[col] = { visible: true, mode: null, prompt: "" };
          return acc;
        },
        {} as Record<string, HeaderControl>
      );

      setHeaderControls((prev) => ({ ...prev, [fileIndex]: initialControls }));
    } catch (error) {
      console.error(`Error processing file ${file.name}:`, error);
    } finally {
      setIsUploading(false);
    }
  };

  const processFolderFiles = async () => {
    if (!folderPath.trim()) {
      setFolderError("Please enter a valid folder path");
      return;
    }

    setIsFolderProcessing(true);
    setFolderError(null);

    try {
      const response = await fetch("http://localhost:5000/getfolderfiles", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ folderPath }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch files from folder");
      }

      const result = await response.json();
      const folderFiles = result.files;

      if (!folderFiles || folderFiles.length === 0) {
        setFolderError("No supported files found in the folder");
        setIsFolderProcessing(false);
        return;
      }

      const supportedFiles = folderFiles.filter(
        (file: string) => file.endsWith(".csv") || file.endsWith(".pdf")
      );

      if (supportedFiles.length === 0) {
        setFolderError("No supported files found in the folder");
        setIsFolderProcessing(false);
        return;
      }

      const startIdx = files.length;
      const newFiles = supportedFiles.map((filePath: string) => {
        const name = filePath.split(/[/\\]/).pop() || "";
        return {
          name,
          path: filePath,
          type: name.endsWith(".csv") ? "text/csv" : "application/pdf",
          size: 0,
        };
      });

      setFiles((prev) => [...prev, ...newFiles]);

      if (activeFileIndex === -1 && newFiles.length > 0) {
        setActiveFileIndex(startIdx);
      }

      const newIndices = Array.from(
        { length: newFiles.length },
        (_, i) => startIdx + i
      );
      setProcessingQueue((prev) => [...prev, ...newIndices]);
    } catch (error) {
      console.error("Error processing folder:", error);
      setFolderError(
        error instanceof Error ? error.message : "Unknown error occurred"
      );
    } finally {
      setIsFolderProcessing(false);
    }
  };

  const handleOutputPathChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOutputPath(e.target.value);
  };

  const dropzoneOptions: DropzoneOptions = { onDrop, multiple: true };
  const { getRootProps, getInputProps, isDragActive } =
    useDropzone(dropzoneOptions);

  const toggleColumnVisibility = (columnId: string) => {
    if (activeFileIndex === -1) return;
    setHeaderControls((prev) => ({
      ...prev,
      [activeFileIndex]: {
        ...prev[activeFileIndex],
        [columnId]: {
          ...prev[activeFileIndex][columnId],
          visible: !prev[activeFileIndex][columnId].visible,
        },
      },
    }));
  };

  const setMode = (columnId: string, mode: "mask" | "obfuscate" | null) => {
    if (activeFileIndex === -1) return;
    setHeaderControls((prev) => ({
      ...prev,
      [activeFileIndex]: {
        ...prev[activeFileIndex],
        [columnId]: {
          ...prev[activeFileIndex][columnId],
          mode,
        },
      },
    }));
  };

  const setPrompt = (columnId: string, prompt: string) => {
    if (activeFileIndex === -1) return;
    setHeaderControls((prev) => ({
      ...prev,
      [activeFileIndex]: {
        ...prev[activeFileIndex],
        [columnId]: {
          ...prev[activeFileIndex][columnId],
          prompt,
        },
      },
    }));
  };

  const switchActiveFile = (index: number) => {
    setActiveFileIndex(index);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const outputFilesList: string[] = [];

      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const fileControls = headerControls[i] || {};
        const selectedHeaders = Object.entries(fileControls)
          .filter(([_, control]) => control.visible)
          .map(([key, control]) => ({
            name: key.replace(/^\d+\.\s/, ""),
            mode: control.mode,
            prompt: control.prompt,
          }));
        const output: SubmitData = {
          fileName: file.name,
          headers: selectedHeaders,
          outputPath: outputPath,
          inputPath: folderPath, // Added inputPath from folderPath
        };
        console.log(`Output for ${file.name}:`, output);

        let response;
        if (file.name.split(".").pop() === "csv") {
          response = await fetch("http://localhost:5000/maskobfcsv", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(output),
          });
        } else {
          // Handle PDF if needed
          continue;
        }

        if (!response.ok) {
          throw new Error(`Network response was not ok for file ${file.name}`);
        }

        const result = await response.json();
        outputFilesList.push(result.filename);
      }

      setOutputFiles(outputFilesList);
      setSubmitResponse(JSON.stringify(outputFilesList, null, 2));
      setJsonOutput(
        JSON.stringify(
          files.map((file, index) => ({
            fileName: file.name,
            headers: Object.entries(headerControls[index] || {})
              .filter(([_, control]) => control.visible)
              .map(([key, control]) => ({
                name: key.replace(/^\d+\.\s/, ""),
                mode: control.mode,
                prompt: control.prompt,
              })),
            outputPath: outputPath,
            inputPath: folderPath, // Included in JSON output for reference
          })),
          null,
          2
        )
      );

      router.push(
        `/outputCsv?files=${encodeURIComponent(
          JSON.stringify(outputFilesList)
        )}`
      );
    } catch (error) {
      console.error("Error:", error);
      setSubmitResponse("Error submitting data to server");
    } finally {
      setIsSubmitting(false);
    }
  };

  const isProcessing = isUploading || processingQueue.length > 0;

  return (
    <div className='container mx-auto p-4 max-w-4xl'>
      <header className='mb-8 text-center'>
        <h1 className='text-3xl font-bold mb-2 flex justify-center'>
          <Shield className='w-16 h-16 text-blue-600 mr-2' />
          <span className='text-6xl font-bold text-gray-200'>Fidelius</span>
        </h1>
        <p className='text-gray-600'></p>
      </header>

      <div className='mb-6 p-4 border rounded-lg bg-gray-50'>
        <h2 className='text-xl font-semibold mb-4'>
          Process Files from Folder
        </h2>
        <div className='flex items-center gap-2'>
          <div className='flex-1'>
            <input
              type='text'
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              placeholder='Enter folder path (e.g., C:\Documents\Data)'
              className='w-full px-3 py-2 border rounded text-sm'
              disabled={isFolderProcessing}
            />
          </div>
          <button
            onClick={processFolderFiles}
            disabled={isFolderProcessing || !folderPath.trim()}
            className='px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2'>
            {isFolderProcessing ? (
              <>
                <Loader2 className='w-4 h-4 animate-spin' />
                Processing...
              </>
            ) : (
              <>
                <FolderOpen className='w-4 h-4' />
                Process Folder
              </>
            )}
          </button>
        </div>
        {folderError && (
          <p className='mt-2 text-sm text-red-500'>{folderError}</p>
        )}
      </div>

      <div className='mb-6 p-4 border rounded-lg bg-gray-50'>
        <h2 className='text-xl font-semibold mb-4'>Specify Output Folder</h2>
        <div className='flex items-center gap-2'>
          <div className='flex-1'>
            <input
              type='text'
              value={outputPath}
              onChange={handleOutputPathChange}
              placeholder='Enter output folder path (e.g., C:\Documents\Output)'
              className='w-full px-3 py-2 border rounded text-sm'
            />
          </div>
          <div className='flex items-center text-sm text-gray-500'>
            <Download className='w-4 h-4 mr-1' />
            Output Location
          </div>
        </div>
      </div>

      <div className='relative flex items-center mb-6'>
        <div className='flex-grow border-t border-gray-300'></div>
        <span className='flex-shrink mx-4 text-gray-400'>OR</span>
        <div className='flex-grow border-t border-gray-300'></div>
      </div>

      {files.length > 0 && (
        <div className='mb-6'>
          <h2 className='text-xl font-semibold mb-4'>Uploaded Files</h2>
          <div className='flex flex-wrap gap-2 mb-4'>
            {files.map((file, index) => {
              const isProcessed = backendColumns[index] !== undefined;
              const isProcessing = processingQueue.includes(index);
              return (
                <button
                  key={index}
                  onClick={() => (isProcessed ? switchActiveFile(index) : null)}
                  className={`px-3 py-1 rounded-md text-sm flex items-center ${
                    activeFileIndex === index
                      ? "bg-blue-500 text-white"
                      : isProcessed
                      ? "bg-gray-200 text-gray-700 hover:bg-gray-300"
                      : "bg-gray-100 text-gray-500 cursor-default"
                  }`}
                  disabled={!isProcessed}>
                  {isProcessing && (
                    <Loader2 className='w-3 h-3 mr-1 animate-spin' />
                  )}
                  {file.name}
                  {isProcessed && (
                    <Check className='w-3 h-3 ml-1 text-green-500' />
                  )}
                </button>
              );
            })}
          </div>

          {isProcessing && (
            <div className='text-sm text-blue-500 mb-2'>
              <Loader2 className='w-4 h-4 mr-1 inline animate-spin' />
              Processing files... ({processingQueue.length} remaining)
            </div>
          )}

          <button
            onClick={() => {
              setFiles([]);
              setBackendColumns({});
              setHeaderControls({});
              setActiveFileIndex(-1);
              setProcessingQueue([]);
            }}
            className='text-sm text-red-500 hover:text-red-700'>
            Clear All Files
          </button>
        </div>
      )}

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 mb-6 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-green-500 bg-green-200"
            : "border-gray-300 hover:border-green-500 hover:bg-green-200"
        }`}>
        <input {...getInputProps()} />
        <div className='flex flex-col items-center justify-center space-y-4'>
          {isProcessing ? (
            <Loader2 className='w-12 h-12 text-blue-500 animate-spin' />
          ) : (
            <Upload className='w-12 h-12 text-gray-400' />
          )}
          {isProcessing ? (
            <p className='text-lg font-medium'>Processing files...</p>
          ) : isDragActive ? (
            <p className='text-lg font-medium'>Drop the files here ...</p>
          ) : (
            <>
              <p className='text-lg font-medium text-gray-500'>
                Drag 'n' drop CSV or PDF files here, or click to select files
              </p>
              <p className='text-sm text-gray-500'>
                Supported file types: CSV, PDF
              </p>
            </>
          )}
        </div>
      </div>

      {activeFileIndex !== -1 &&
        backendColumns[activeFileIndex]?.length > 0 && (
          <div className='space-y-4'>
            <h2 className='text-xl font-semibold'>
              Detected PII in {files[activeFileIndex].name}
            </h2>
            <div className='overflow-x-auto'>
              <table className='min-w-full'>
                <thead>
                  <tr>
                    <th className='px-4 py-2 text-left text-sm font-medium text-gray-200'>
                      Check
                    </th>
                    <th className='px-4 py-2 text-left text-sm font-medium text-gray-200'>
                      Header
                    </th>
                    <th className='px-4 py-2 text-left text-sm font-medium text-gray-200'>
                      Mode
                    </th>
                    <th className='px-4 py-2 text-left text-sm font-medium text-gray-200'>
                      Prompt
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {backendColumns[activeFileIndex].map((column) => {
                    const control = headerControls[activeFileIndex]?.[
                      column
                    ] || {
                      visible: true,
                      mode: null,
                      prompt: "",
                    };
                    return (
                      <tr
                        key={column}
                        className={control.visible ? "" : "opacity-50"}>
                        <td className='px-4 py-2 text-sm text-gray-900'>
                          <button
                            onClick={() => toggleColumnVisibility(column)}
                            className='p-1 rounded-full hover:bg-gray-200'
                            aria-label={
                              control.visible ? "Hide column" : "Show column"
                            }>
                            {control.visible ? (
                              <Check className='w-5 h-5 text-green-500' />
                            ) : (
                              <X className='w-5 h-5 text-red-500' />
                            )}
                          </button>
                        </td>
                        <td className='px-4 py-2 text-sm text-gray-200'>
                          {column.replace(/^\d+\.\s/, "")}
                        </td>
                        <td className='px-4 py-2 text-sm text-gray-200'>
                          <div className='flex items-center space-x-4'>
                            <label className='flex items-center'>
                              <input
                                type='radio'
                                checked={control.mode === "mask"}
                                onChange={() => setMode(column, "mask")}
                                className='form-radio h-4 w-4 text-blue-600'
                              />
                              <span className='ml-2'>Mask</span>
                            </label>
                            <label className='flex items-center'>
                              <input
                                type='radio'
                                checked={control.mode === "obfuscate"}
                                onChange={() => setMode(column, "obfuscate")}
                                className='form-radio h-4 w-4 text-blue-600'
                              />
                              <span className='ml-2'>Obfuscate</span>
                            </label>
                          </div>
                        </td>
                        <td className='px-4 py-2 text-sm text-gray-900'>
                          <input
                            type='text'
                            value={control.prompt}
                            onChange={(e) => setPrompt(column, e.target.value)}
                            placeholder='Enter prompt'
                            className='w-full px-2 py-1 text-sm border rounded'
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <div className='flex justify-end'>
              <button
                onClick={handleSubmit}
                disabled={
                  isSubmitting || files.length === 0 || !outputPath.trim()
                }
                className='px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'>
                {isSubmitting ? "Submitting..." : "Submit"}
              </button>
            </div>
            {!outputPath.trim() && files.length > 0 && (
              <p className='mt-2 text-sm text-red-500'>
                Please specify an output folder before submitting.
              </p>
            )}
            {jsonOutput && (
              <div className='mt-4'>
                <h3 className='text-lg font-semibold mb-2'>JSON Output:</h3>
                <pre className='p-4 rounded overflow-x-auto text-gray-200 bg-gray-800'>
                  {jsonOutput}
                </pre>
              </div>
            )}
            {submitResponse && (
              <div className='mt-4'>
                <h3 className='text-lg font-semibold mb-2'>Server Response:</h3>
                <pre className='p-4 rounded overflow-x-auto text-gray-200 bg-gray-800'>
                  {submitResponse}
                </pre>
              </div>
            )}
          </div>
        )}
    </div>
  );
}
