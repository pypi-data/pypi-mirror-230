# Doc Analyzer

Doc Analyzer contains classes simplifying some text-based AI workflows. Text-based AI workflows often contain multiple steps, such as: reading in the source file; processing it to extract raw text or text fragments; loading those text fragments into an index or embeddings; and then querying that store. Tools like Llama index provide interfaces for each of these steps, and the resulting code is often disconnected and scattered around a program. Additionally, prepocessing steps often generate intermediate files that have to be persisted, and that can be difficult and timeconsuming to reproduce.

