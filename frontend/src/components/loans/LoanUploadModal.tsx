import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, X } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import api from '../../lib/api';
import { toast } from 'react-hot-toast';

interface LoanUploadModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: () => void;
}

export function LoanUploadModal({ isOpen, onClose, onSuccess }: LoanUploadModalProps) {
    const [file, setFile] = useState<File | null>(null);
    const [title, setTitle] = useState('');
    const [borrowerName, setBorrowerName] = useState('');
    const [isUploading, setIsUploading] = useState(false);

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
        }
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { 'application/pdf': ['.pdf'] },
        maxFiles: 1,
        multiple: false
    });

    const handleUpload = async () => {
        if (!file || !title) return;

        setIsUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        if (borrowerName) formData.append('borrower_name', borrowerName);

        try {
            await api.post('/api/loans/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            toast.success('Loan uploaded successfully');
            setFile(null);
            setTitle('');
            setBorrowerName('');
            onSuccess();
            onClose();
        } catch (error: any) {
            console.error('Upload failed:', error);
            toast.error('Failed to upload loan');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose} title="Upload Loan Agreement">
            <div className="space-y-6">
                {/* Dropzone */}
                {!file ? (
                    <div
                        {...getRootProps()}
                        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-black bg-gray-50' : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'}`}
                    >
                        <input {...getInputProps()} />
                        <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 text-gray-400">
                            <Upload className="w-6 h-6" />
                        </div>
                        <p className="text-sm font-medium text-black mb-1">
                            {isDragActive ? 'Drop PDF here' : 'Click to upload or drag & drop'}
                        </p>
                        <p className="text-xs text-gray-500">
                            PDF only, max 10MB
                        </p>
                    </div>
                ) : (
                    <div className="flex items-center justify-between p-3 bg-gray-50 border border-gray-200 rounded-lg">
                        <div className="flex items-center gap-3 overflow-hidden">
                            <div className="w-10 h-10 bg-white border border-gray-200 rounded-lg flex items-center justify-center shrink-0 text-red-500">
                                <FileText className="w-5 h-5" />
                            </div>
                            <div className="min-w-0">
                                <p className="text-sm font-medium text-black truncate">{file.name}</p>
                                <p className="text-xs text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                        </div>
                        <button
                            onClick={() => setFile(null)}
                            className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                            disabled={isUploading}
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                )}

                {/* Inputs */}
                <div className="space-y-4">
                    <Input
                        label="Loan Title *"
                        placeholder="e.g. Facility Agreement 2024"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        disabled={isUploading}
                    />
                    <Input
                        label="Borrower Name (Optional)"
                        placeholder="e.g. ACME Corp"
                        value={borrowerName}
                        onChange={(e) => setBorrowerName(e.target.value)}
                        disabled={isUploading}
                    />
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-2">
                    <Button variant="ghost" onClick={onClose} disabled={isUploading}>Cancel</Button>
                    <Button
                        onClick={handleUpload}
                        disabled={!file || !title || isUploading}
                        loading={isUploading}
                    >
                        {isUploading ? 'Uploading & Extracting...' : 'Upload & Extract'}
                    </Button>
                </div>
            </div>
        </Modal>
    );
}
