"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  Loader2,
  Table as TableIcon,
  Shield,
  FileText,
  ChevronLeft,
  ChevronRight,
  Download,
} from "lucide-react";
import { parse } from "papaparse";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  ColumnDef,
  getPaginationRowModel,
} from "@tanstack/react-table";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

interface CsvData {
  headers: string[];
  rows: any[];
  filename: string;
}

export default function MultiFileCsvViewer() {
  const [csvDatasets, setCsvDatasets] = useState<CsvData[]>([]);
  const [selectedFileIndex, setSelectedFileIndex] = useState<number>(0);
  const [columnVisibility, setColumnVisibility] = useState<
    Record<string, boolean>
  >({});
  const [loading, setLoading] = useState(true);
  const searchParams = useSearchParams();

  useEffect(() => {
    const loadCsvFiles = async () => {
      setLoading(true);
      const filesParam = searchParams.get("files");
      if (!filesParam) {
        setLoading(false);
        return;
      }

      try {
        const outputFiles: string[] = JSON.parse(
          decodeURIComponent(filesParam)
        );
        const datasets: CsvData[] = [];

        for (const filename of outputFiles) {
          const filePath = `/${filename}`; // Assumes files are in public directory
          const response = await fetch(filePath);

          if (!response.ok) {
            console.error(
              `Failed to fetch ${filename}: ${response.statusText}`
            );
            continue;
          }

          const csvText = await response.text();
          const result = (await new Promise((resolve) => {
            parse(csvText, {
              header: true,
              skipEmptyLines: true,
              complete: resolve,
            });
          })) as any;

          datasets.push({
            headers: result.meta.fields || [],
            rows: result.data,
            filename: filename,
          });
        }

        setCsvDatasets(datasets);

        if (datasets.length > 0) {
          const initialVisibility = datasets[0].headers.reduce(
            (acc, header) => {
              acc[header] = true;
              return acc;
            },
            {} as Record<string, boolean>
          );
          setColumnVisibility(initialVisibility);
        }
      } catch (error) {
        console.error("Error loading CSV files:", error);
      } finally {
        setLoading(false);
      }
    };

    loadCsvFiles();
  }, [searchParams]);

  const table = useReactTable({
    data: csvDatasets[selectedFileIndex]?.rows || [],
    columns: (csvDatasets[selectedFileIndex]?.headers || []).map((header) => ({
      accessorKey: header,
      header: header,
    })),
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    state: { columnVisibility },
    onColumnVisibilityChange: setColumnVisibility,
  });

  const memoizedTable = useMemo(() => table, [table]);

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center h-screen bg-gray-50">
        <Shield className="w-16 h-16 text-blue-500 mb-4" />
        <Loader2 className="w-8 h-8 animate-spin text-blue-600 mb-2" />
        <p className="text-gray-700 font-medium">Loading processed files...</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2 flex justify-center items-center">
          <Shield className="w-12 h-12 text-blue-500 mr-2" />
          <span className="text-4xl font-bold text-blue-600">Fidelius</span>
        </h1>
        <p className="text-gray-500 font-light italic">Protected Data Viewer</p>
      </header>

      {csvDatasets.length === 0 ? (
        <div className="text-center p-12 bg-white rounded-lg shadow-sm border">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-700 text-lg mb-4">
            No processed files available to display.
          </p>
          <Link
            href="/readFile"
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium inline-flex items-center"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Return to File Processing
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <TableIcon className="w-5 h-5 text-blue-500" />
                <h2 className="text-xl font-semibold text-gray-800">
                  Processed Files
                </h2>
              </div>
              <div className="flex items-center space-x-4">
                <label className="text-sm text-gray-600">Select File:</label>
                <select
                  value={selectedFileIndex}
                  onChange={(e) => {
                    const newIndex = Number(e.target.value);
                    setSelectedFileIndex(newIndex);
                    const newVisibility = csvDatasets[newIndex].headers.reduce(
                      (acc, header) => {
                        acc[header] = true;
                        return acc;
                      },
                      {} as Record<string, boolean>
                    );
                    setColumnVisibility(newVisibility);
                  }}
                  className="min-w-[200px] px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-700 
                    focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                    hover:border-gray-400 transition-colors"
                >
                  {csvDatasets.map((dataset, index) => (
                    <option key={index} value={index}>
                      {dataset.filename}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="bg-gray-50 rounded-md p-3 mb-4 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {csvDatasets[selectedFileIndex]?.rows.length || 0} rows
                and {csvDatasets[selectedFileIndex]?.headers.length || 0}{" "}
                columns
              </div>
              <button
                className="text-blue-600 hover:text-blue-800 transition-colors flex items-center text-sm font-medium"
                onClick={() => {
                  /* Add download functionality */
                }}
              >
                <Download className="w-4 h-4 mr-1" />
                Download CSV
              </button>
            </div>

            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  {memoizedTable.getHeaderGroups().map((headerGroup) => (
                    <tr key={headerGroup.id}>
                      {headerGroup.headers.map((header) => (
                        <th
                          key={header.id}
                          className="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b"
                        >
                          {flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                        </th>
                      ))}
                    </tr>
                  ))}
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {memoizedTable.getRowModel().rows.map((row) => (
                    <tr
                      key={row.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      {row.getVisibleCells().map((cell) => (
                        <td
                          key={cell.id}
                          className="px-6 py-4 text-sm text-gray-700 whitespace-nowrap"
                        >
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext()
                          )}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-4 flex items-center justify-between">
              <button
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
                className="px-4 py-2 flex items-center space-x-2 text-gray-700 bg-white border border-gray-300 rounded-md 
                  hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>
              <span className="text-sm text-gray-600">
                Page {table.getState().pagination.pageIndex + 1} of{" "}
                {table.getPageCount()}
              </span>
              <button
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
                className="px-4 py-2 flex items-center space-x-2 text-gray-700 bg-white border border-gray-300 rounded-md 
                  hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          <div className="flex justify-center">
            <Link
              href="/readFile"
              className="text-blue-600 hover:text-blue-800 transition-colors font-medium flex items-center"
            >
              <ChevronLeft className="w-4 h-4 mr-1" />
              Return to File Processing
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
