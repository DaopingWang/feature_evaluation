import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;

import java.io.*;
import java.util.*;

public class csv_parser {

    private static HashMap<String, Article> articleHashMap = new HashMap<>();
    private static HashMap<String, HashMap<String, Article>> duplicateSetHashMap = new HashMap<>();
    private static HashMap<String, Article> mergedHashMap = new HashMap<>();

    private static final String dataPath = "C:/Users/wang.daoping/Documents/feature data/";
    private static final String tabletsMercateoKeywordFilepath = dataPath + "tablets_article_mercateo_keywords.dat";
    private static final String articleFeatureValueFilepath = dataPath + "tablets_article_feature_value.dat";
    private static final String priceDataFilepath = dataPath + "tablets_article_price_data.dat";
    private static final String baseDataFilepath = dataPath + "tablets_article_base_data.dat";
    private static final String duplicateFilepath = dataPath + "tablets_article_duplicate_relation.dat";

    private static List<String> tabletKeywordList = new ArrayList<>();
    private static List<String> tabletFeatureList = new ArrayList<>();

    private static void collectArticles() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(tabletsMercateoKeywordFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(isTablet(lineBuffer[2])) articleHashMap.put(lineBuffer[1], new Article(lineBuffer[1]));
        }
    }

    private static void collectDuplicateRelations() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(duplicateFilepath),
                "Cp1252"), '\t', '\"', 1);
        while ((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            Article article = articleHashMap.get(lineBuffer[1]);
            String setID = lineBuffer[2];
            if(!duplicateSetHashMap.containsKey(setID)){
                HashMap<String, Article> thisSetHashMap = new HashMap<>();
                thisSetHashMap.put(lineBuffer[1], article);
                duplicateSetHashMap.put(setID, thisSetHashMap);
            } else {
                duplicateSetHashMap.get(setID).put(lineBuffer[1], article);
            }
        }
    }

    private static void collectFeatureValues() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(articleFeatureValueFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addFeature(lineBuffer[2], lineBuffer[3]);
        }
    }

    private static void collectBaseValues() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(baseDataFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addFeature("brand", lineBuffer[7]);
        }
    }

    private static void collectPriceData() throws IOException {
        String[] lineBuffer;
        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(priceDataFilepath),
                "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null){
            if(!articleHashMap.containsKey(lineBuffer[1])) continue;
            articleHashMap.get(lineBuffer[1]).addPrice(Float.parseFloat(lineBuffer[2]));
        }
    }

    private static boolean isTablet(String keyword) {
        return tabletKeywordList.contains(keyword);
    }

    private static void writeRawCSV() throws IOException {
        String filename = "tablets_training_data.csv";
        CSVWriter writer = new CSVWriter(new OutputStreamWriter(new FileOutputStream(dataPath + filename),
                "Cp1252"), '\t', CSVWriter.NO_QUOTE_CHARACTER, CSVWriter.NO_ESCAPE_CHARACTER);

        StringBuilder lineBuffer = new StringBuilder("set_id\tarticle_id\tprice");
        for(String feature : tabletFeatureList){
            lineBuffer.append("\t");
            lineBuffer.append(feature);
        }
        String[] rec = lineBuffer.toString().split("\t");
        writer.writeNext(rec);

        for(Map.Entry<String, HashMap<String, Article>> iterator : duplicateSetHashMap.entrySet()){
            for(Map.Entry<String, Article> _iterator : iterator.getValue().entrySet()){
                String id = iterator.getKey() + "\t" + _iterator.getKey() + "\t" + _iterator.getValue().getAvgPrice();
                lineBuffer = new StringBuilder(id);
                for(String featureName : tabletFeatureList){
                    lineBuffer.append("\t");
                    lineBuffer.append(_iterator.getValue().features.get(featureName)); // care NaN!
                }
                rec = lineBuffer.toString().split("\t");
                writer.writeNext(rec);
            }
        }
        writer.close();
    }

    private static void writeMergedCSV() throws IOException {
        String filename = "tablets_merged_data.csv";
        CSVWriter writer = new CSVWriter(new OutputStreamWriter(new FileOutputStream(dataPath + filename),
                "Cp1252"), ',', CSVWriter.NO_QUOTE_CHARACTER, CSVWriter.NO_ESCAPE_CHARACTER);

        StringBuilder lineBuffer = new StringBuilder("set_id\tprice");
        for(String feature : tabletFeatureList){
            lineBuffer.append("\t");
            lineBuffer.append(feature);
        }
        String[] rec = lineBuffer.toString().split("\t");
        writer.writeNext(rec);

        for(Map.Entry<String, Article> iterator : mergedHashMap.entrySet()){
            float avg_price;
            if (( avg_price= iterator.getValue().getAvgPrice()) == -1) continue;
            String id = iterator.getKey() + "\t" + Float.toString(avg_price);
            lineBuffer = new StringBuilder(id);
            for(String featureName : tabletFeatureList){
                lineBuffer.append("\t");
                lineBuffer.append(iterator.getValue().features.get(featureName)); // care NaN!
            }
            rec = lineBuffer.toString().split("\t");
            writer.writeNext(rec);
        }

        writer.close();
    }

    private static void mergeDuplicates() throws IOException {
        for(Map.Entry<String, HashMap<String, Article>> iterator : duplicateSetHashMap.entrySet()){
            Article mergedArticle = new Article(iterator.getKey());
            for(Map.Entry<String, Article> _iterator : iterator.getValue().entrySet()){
                Article currentArticle = _iterator.getValue();
                for(Map.Entry<String, String> __iterator : currentArticle.features.entrySet()){
                    if (!mergedArticle.features.containsKey(__iterator.getKey())){
                        mergedArticle.features.put(__iterator.getKey(), __iterator.getValue());
                    } else if (!mergedArticle.features.containsValue(__iterator.getValue())){
                        //TODO
                    }
                    mergedArticle.addPrice(currentArticle.getAvgPrice());
                }
            }
            mergedHashMap.put(iterator.getKey(), mergedArticle);
        }
    }

    public static void main(String[] args){
        tabletKeywordList.add("Tablet");
        tabletKeywordList.add("Tablet PC");
        tabletKeywordList.add("TabletPC");
        tabletKeywordList.add("2-in-1 Tablet");
        tabletKeywordList.add("Hybrid-Tablet");
        tabletKeywordList.add("Tab Samsung");

        tabletFeatureList.add("brand");
        tabletFeatureList.add("Betriebssystem");
        tabletFeatureList.add("SpeicherkapazitÃ¤t");
        tabletFeatureList.add("Arbeitsspeicher");
        tabletFeatureList.add("CPU-Taktfrequenz");
        tabletFeatureList.add("Bilddiagonale");
        tabletFeatureList.add("AuflÃ¶sung");
        tabletFeatureList.add("Festplatte");
        tabletFeatureList.add("AkkukapazitÃ¤t");
        tabletFeatureList.add("AuflÃ¶sung Hauptkamera");
        tabletFeatureList.add("SSD-SpeicherkapazitÃ¤t");
        tabletFeatureList.add("Grafik-Controller-Serie");

        try {
            collectArticles();
            collectFeatureValues();
            collectPriceData();
            collectBaseValues();
            collectDuplicateRelations();
            mergeDuplicates();
            //writeRawCSV();
            writeMergedCSV();
        } catch (IOException e){
            e.printStackTrace();
        }
        System.out.println(duplicateSetHashMap.size());
    }
}
