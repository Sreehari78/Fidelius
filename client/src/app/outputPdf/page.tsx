"use client";

import React, { useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";
import "react-pdf/dist/esm/Page/TextLayer.css";

// Set up the worker for pdf.js
pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

// You can change the path to your PDF file here
const pdfFilePath = "/modified.pdf"; // Ensure this file is located in the public folder

const PdfViewer = () => {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  return (
    <div className='flex flex-col min-h-screen bg-gray-900 text-gray-200'>
      <header className='py-6 px-4 bg-gray-800'>
        <div className='container mx-auto'>
          <h1 className='text-3xl font-bold mb-2'>PDF Viewer</h1>
          <p className='text-gray-400'>
            View and navigate through PDF documents
          </p>
        </div>
      </header>

      <main className='flex-grow container mx-auto px-4 py-8'>
        <div
          className='bg-white rounded-lg shadow-lg overflow-hidden p-4'
          style={{ height: "calc(100vh - 200px)" }}>
          <Document
            file={pdfFilePath}
            onLoadSuccess={onDocumentLoadSuccess}
            className='flex flex-col items-center'>
            <Page
              pageNumber={pageNumber}
              renderTextLayer={true}
              renderAnnotationLayer={true}
              className='mb-4'
            />
            <div className='text-gray-800'>
              <p>
                Page {pageNumber} of {numPages}
              </p>
              <button
                onClick={() => setPageNumber((page) => Math.max(page - 1, 1))}
                disabled={pageNumber <= 1}
                className='bg-blue-500 text-white px-4 py-2 rounded mr-2 disabled:bg-gray-400'>
                Previous
              </button>
              <button
                onClick={() =>
                  setPageNumber((page) => Math.min(page + 1, numPages || page))
                }
                disabled={pageNumber >= (numPages || 1)}
                className='bg-blue-500 text-white px-4 py-2 rounded disabled:bg-gray-400'>
                Next
              </button>
            </div>
          </Document>
        </div>
      </main>

      <footer className='py-4 bg-gray-800 text-center text-gray-400'>
        <p>
          &copy; {new Date().getFullYear()} PDF Viewer. All rights reserved.
        </p>
      </footer>
    </div>
  );
};

export default PdfViewer;
