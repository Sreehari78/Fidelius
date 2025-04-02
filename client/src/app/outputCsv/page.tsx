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
          const filePath = `/${filename}`;
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
      <div className='flex justify-center items-center h-screen'>
        <Loader2 className='w-8 h-8 animate-spin text-blue-500' />
      </div>
    );
  }

  return (
    <div className='container mx-auto p-4 max-w-6xl'>
      <header className='mb-8 text-center'>
        <h1 className='text-3xl font-bold mb-2 text-gray-100'>
          Modified Files Viewer
        </h1>
        <p className='text-gray-400'>Viewing modified CSV files</p>
      </header>

      {csvDatasets.length === 0 ? (
        <div className='text-center'>
          <p className='text-gray-400'>
            No modified files available to display.
          </p>
        </div>
      ) : (
        <>
          <div className='mb-6 p-6 rounded-lg bg-white/5 backdrop-blur-sm'>
            <div className='flex items-center gap-2'>
              <label className='text-gray-300 mr-2'>Select File:</label>
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
                className='flex-1 px-4 py-2.5 rounded-md text-gray-100 bg-black/20 border border-white/10 focus:outline-none focus:border-blue-500'>
                {csvDatasets.map((dataset, index) => (
                  <option key={index} value={index} className='bg-gray-800'>
                    {dataset.filename}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className='overflow-x-auto rounded-lg bg-white/5 backdrop-blur-sm'>
            <table className='min-w-full border-collapse'>
              <thead>
                {memoizedTable.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map((header) => (
                      <th
                        key={header.id}
                        className='px-4 py-3 text-left text-sm font-medium text-gray-300 border-b border-white/5 bg-black/10'>
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
                  <tr key={row.id} className='hover:bg-white/5'>
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className='px-4 py-3 text-sm text-gray-300 border-b border-white/10'>
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

          <div className='mt-6 flex justify-between items-center p-4 rounded-lg bg-white/5 backdrop-blur-sm'>
            <button
              className='px-4 py-2 rounded-md bg-blue-500/80 text-white hover:bg-blue-600/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}>
              Previous
            </button>
            <span className='text-gray-300'>
              Page {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount()}
            </span>
            <button
              className='px-4 py-2 rounded-md bg-blue-500/80 text-white hover:bg-blue-600/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed'
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
