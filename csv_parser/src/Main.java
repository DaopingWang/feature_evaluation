/**
 * Created by Wang.Daoping on 04.05.2017.
 */

import com.opencsv.*;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

public class Main {

    static ArrayList<String> tablet_keywords = new ArrayList<>();

    public static void main(String[] args){
        ArrayList<Article> article_list = new ArrayList<>();

        tablet_keywords.add("Tablet");
        tablet_keywords.add("Tablet PC");
        tablet_keywords.add("TabletPC");
        tablet_keywords.add("2-in-1 Tablet");
        tablet_keywords.add("Hybrid-Tablet");
        tablet_keywords.add("Tab Samsung");

        String feature_data_path = "C:/Users/wang.daoping/Documents/feature data/";
        String tablet_article_keywords_file = feature_data_path + "tablets_article_mercateo_keywords.dat";
        String article_feature_value_file = feature_data_path + "tablets_article_feature_value.dat";

        try {
            collectTabletArticles(tablet_article_keywords_file, article_list);
            collectFeatureValues(article_list, article_feature_value_file);
        } catch (IOException e){
            e.printStackTrace();
        }

        for(int i = 0; i < article_list.size(); i++){
            System.out.println(i + "\t" + article_list.get(i).getArticleID());
        }
    }

    public static void collectTabletArticles(String tablet_article_keywords_file, ArrayList<Article> article_list) throws IOException{
        String[] lineBuffer;

        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(tablet_article_keywords_file), "Cp1252"), '\t', '\"', 1);
        while((lineBuffer = reader.readNext()) != null) {
            if(isTablet(lineBuffer[2])){
                pushList(lineBuffer[1], article_list);
            }
        }
    }

    public static void collectFeatureValues(ArrayList<Article> article_list, String article_feature_value_file) throws IOException{
        String[] lineBuffer;

        CSVReader reader = new CSVReader(new InputStreamReader(new FileInputStream(article_feature_value_file), "Cp1252"), '\t', '\"', 1);
        while ((lineBuffer = reader.readNext()) != null){
            for(int i = 0; i < article_list.size(); i++){
                if(article_list.get(i).getArticleID().equals(lineBuffer[1])){
                    switch (lineBuffer.length){
                        case 3:
                            article_list.get(i).addFeature(lineBuffer[2]);
                            break;
                        case 4:
                            article_list.get(i).addFeature(lineBuffer[2], lineBuffer[3]);
                            break;
                        default:
                            System.out.println("collectFeatureValues: unexpected lineBuffer length: " + Integer.toString(lineBuffer.length));
                            System.exit(666);
                    }
                    break;
                }
            }
        }

        // Remove articles with no feature information
        for(int i = 0; i < article_list.size(); i++){
            if(article_list.get(i).getNumFeatures() == 0){
                article_list.remove(i);
                i--;
            }
        }
    }

    public static boolean pushList(String article_id, ArrayList<Article> list){
        ArrayList<String> importedArticles = new ArrayList<>();
        for(int i = 0; i < list.size(); i++){
            importedArticles.add(list.get(i).getArticleID());
        }
        if(importedArticles.contains(article_id)) return true;
        else {
            Article article = new Article(article_id);
            list.add(article);
        }
        return true;
    }

    public static boolean isTablet(String keyword){
        return tablet_keywords.contains(keyword);
    }
}
