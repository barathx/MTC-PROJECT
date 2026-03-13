using System;
using System.IO;
using System.Threading.Tasks;
using Windows.Media.Ocr;
using Windows.Graphics.Imaging;
using Windows.Storage;
using Windows.Storage.Streams;

class Program {
    static async Task Main(string[] args) {
        if (args.Length == 0) {
            Console.WriteLine("Usage: winocr.exe <image_path>");
            return;
        }
        string path = args[0];
        try {
            var file = await StorageFile.GetFileFromPathAsync(Path.GetFullPath(path));
            using (var stream = await file.OpenAsync(FileAccessMode.Read)) {
                var decoder = await BitmapDecoder.CreateAsync(stream);
                using (var bitmap = await decoder.GetSoftwareBitmapAsync()) {
                    var engine = OcrEngine.TryCreateFromUserProfileLanguages();
                    if (engine == null) {
                        Console.WriteLine("OCR_ERROR: No OCR engine available");
                        return;
                    }
                    var result = await engine.RecognizeAsync(bitmap);
                    Console.WriteLine(result.Text);
                }
            }
        } catch (Exception ex) {
            Console.WriteLine("OCR_ERROR: " + ex.Message);
        }
    }
}
