"use client";

import React, { useState, useEffect, useMemo } from "react";
import { Loader2, Table as TableIcon } from "lucide-react";
import { parse } from "papaparse";
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  ColumnDef,
  getPaginationRowModel,
} from "@tanstack/react-table";
import { useSearchParams } from "next/navigation";

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
      <div className="flex justify-center items-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 bg-gray-900">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold mb-2">Modified Files Viewer</h1>
        <p className="text-gray-600">Viewing modified CSV files</p>
      </header>

      {csvDatasets.length === 0 ? (
        <div className="text-center">
          <p className="text-gray-600">
            No modified files available to display.
          </p>
        </div>
      ) : (
        <>
          <div className="mb-6 bg-white rounded-lg shadow-sm border p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <TableIcon className="w-5 h-5 text-blue-500" />
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-1">
                    Select File to View
                  </label>
                  <p className="text-xs text-gray-500">
                    Choose a processed CSV file to display
                  </p>
                </div>
              </div>
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
                className="min-w-[250px] px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-gray-700 
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                hover:border-gray-400 transition-colors cursor-pointer"
              >
                {csvDatasets.map((dataset, index) => (
                  <option key={index} value={index} className="py-1">
                    {dataset.filename}
                  </option>
                ))}
              </select>
            </div>
            <div className="mt-3 text-sm text-gray-500">
              Showing {csvDatasets[selectedFileIndex]?.rows.length || 0} rows
              and {csvDatasets[selectedFileIndex]?.headers.length || 0} columns
            </div>
          </div>

          <div className="overflow-x-auto bg-white rounded-lg shadow-sm border">
            <table className="min-w-full border-collapse border border-gray-200">
              <thead>
                {memoizedTable.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className="px-4 py-2 text-left text-sm font-medium text-gray-700 border"
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
              <tbody>
                {memoizedTable.getRowModel().rows.map((row) => (
                  <tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className="px-4 py-2 text-sm text-gray-700 border"
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

          <div className="mt-4 flex justify-between">
            <button
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </button>
            <span>
              Page {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount()}
            </span>
            <button
              className="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
