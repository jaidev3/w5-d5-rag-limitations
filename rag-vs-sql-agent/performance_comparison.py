"""
Performance Comparison Script for RAG vs SQL Agent
This script runs comprehensive performance tests and generates comparison reports.
"""

import json
import time
from typing import Dict, List, Any
from datetime import datetime
import os
import sys

# Import our systems
from rag_system import ChinookRAGSystem, PerformanceTester as RAGTester
from sql_agent_enhanced import EnhancedSQLAgent, SQLPerformanceTester
from test_questions import get_sample_questions, evaluate_answer_quality, benchmark_performance

class ComprehensiveComparison:
    """Comprehensive comparison between RAG and SQL Agent systems"""
    
    def __init__(self):
        print("Initializing systems...")
        
        # Initialize both systems
        try:
            self.rag_system = ChinookRAGSystem()
            self.sql_agent = EnhancedSQLAgent()
            print("✓ Both systems initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing systems: {e}")
            sys.exit(1)
        
        # Initialize testers
        self.rag_tester = RAGTester(self.rag_system)
        self.sql_tester = SQLPerformanceTester(self.sql_agent)
        
        # Results storage
        self.comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "rag_results": [],
            "sql_results": [],
            "summary": {},
            "detailed_analysis": {}
        }
    
    def run_performance_tests(self, test_questions: List[str]) -> Dict[str, Any]:
        """Run performance tests on both systems"""
        
        print(f"\n{'='*60}")
        print("PERFORMANCE COMPARISON: RAG vs SQL Agent")
        print(f"{'='*60}")
        print(f"Testing {len(test_questions)} questions...")
        
        # Test RAG system
        print(f"\n{'-'*30}")
        print("Testing RAG System")
        print(f"{'-'*30}")
        
        rag_results = []
        for i, question in enumerate(test_questions, 1):
            print(f"RAG Question {i}/{len(test_questions)}: {question[:50]}...")
            
            try:
                result = self.rag_system.query(question)
                
                # Evaluate answer quality
                evaluation = evaluate_answer_quality(question, result.answer)
                
                test_result = {
                    "question": question,
                    "answer": result.answer,
                    "response_time": result.response_time,
                    "confidence_score": result.confidence_score,
                    "retrieved_docs_count": len(result.retrieved_docs),
                    "evaluation": evaluation,
                    "timestamp": datetime.now().isoformat()
                }
                
                rag_results.append(test_result)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                rag_results.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "response_time": 0,
                    "confidence_score": 0,
                    "error": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Test SQL Agent system
        print(f"\n{'-'*30}")
        print("Testing SQL Agent System")
        print(f"{'-'*30}")
        
        sql_results = []
        for i, question in enumerate(test_questions, 1):
            print(f"SQL Question {i}/{len(test_questions)}: {question[:50]}...")
            
            try:
                result = self.sql_agent.query(question, method="agent")
                
                # Evaluate answer quality
                evaluation = evaluate_answer_quality(question, result.answer)
                
                test_result = {
                    "question": question,
                    "answer": result.answer,
                    "response_time": result.response_time,
                    "sql_query": result.sql_query,
                    "tool_calls_made": result.tool_calls_made,
                    "error_occurred": result.error_occurred,
                    "evaluation": evaluation,
                    "timestamp": datetime.now().isoformat()
                }
                
                sql_results.append(test_result)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                sql_results.append({
                    "question": question,
                    "answer": f"Error: {str(e)}",
                    "response_time": 0,
                    "error": True,
                    "timestamp": datetime.now().isoformat()
                })
        
        # Store results
        self.comparison_results["rag_results"] = rag_results
        self.comparison_results["sql_results"] = sql_results
        
        return self.comparison_results
    
    def analyze_results(self) -> Dict[str, Any]:
        """Analyze and compare the results"""
        
        rag_results = self.comparison_results["rag_results"]
        sql_results = self.comparison_results["sql_results"]
        
        # Calculate metrics for RAG system
        rag_metrics = self._calculate_metrics(rag_results, "rag")
        
        # Calculate metrics for SQL Agent system
        sql_metrics = self._calculate_metrics(sql_results, "sql")
        
        # Comparative analysis
        comparison = self._comparative_analysis(rag_metrics, sql_metrics)
        
        analysis = {
            "rag_metrics": rag_metrics,
            "sql_metrics": sql_metrics,
            "comparison": comparison,
            "recommendations": self._generate_recommendations(comparison)
        }
        
        self.comparison_results["detailed_analysis"] = analysis
        return analysis
    
    def _calculate_metrics(self, results: List[Dict], system_type: str) -> Dict[str, Any]:
        """Calculate performance metrics for a system"""
        
        if not results:
            return {}
        
        # Filter out error results
        valid_results = [r for r in results if not r.get("error", False)]
        error_count = len(results) - len(valid_results)
        
        if not valid_results:
            return {
                "total_questions": len(results),
                "error_rate": 1.0,
                "valid_responses": 0
            }
        
        # Response time metrics
        response_times = [r["response_time"] for r in valid_results]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        # Accuracy metrics (where evaluation is available)
        evaluated_results = [r for r in valid_results if r.get("evaluation", {}).get("evaluated", False)]
        accuracy_scores = [r["evaluation"]["score"] for r in evaluated_results]
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0
        
        # System-specific metrics
        if system_type == "rag":
            confidence_scores = [r.get("confidence_score", 0) for r in valid_results]
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            
            system_specific = {
                "avg_confidence_score": avg_confidence,
                "min_confidence": min(confidence_scores),
                "max_confidence": max(confidence_scores)
            }
        else:  # SQL
            tool_calls = [r.get("tool_calls_made", 0) for r in valid_results]
            avg_tool_calls = sum(tool_calls) / len(tool_calls)
            
            system_specific = {
                "avg_tool_calls": avg_tool_calls,
                "min_tool_calls": min(tool_calls),
                "max_tool_calls": max(tool_calls)
            }
        
        metrics = {
            "total_questions": len(results),
            "valid_responses": len(valid_results),
            "error_count": error_count,
            "error_rate": error_count / len(results),
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "avg_accuracy": avg_accuracy,
            "evaluated_questions": len(evaluated_results),
            **system_specific
        }
        
        return metrics
    
    def _comparative_analysis(self, rag_metrics: Dict, sql_metrics: Dict) -> Dict[str, Any]:
        """Perform comparative analysis between systems"""
        
        comparison = {}
        
        # Response time comparison
        if rag_metrics.get("avg_response_time") and sql_metrics.get("avg_response_time"):
            rag_time = rag_metrics["avg_response_time"]
            sql_time = sql_metrics["avg_response_time"]
            
            comparison["response_time"] = {
                "rag_faster": rag_time < sql_time,
                "speed_difference": abs(rag_time - sql_time),
                "speed_ratio": max(rag_time, sql_time) / min(rag_time, sql_time)
            }
        
        # Accuracy comparison
        if rag_metrics.get("avg_accuracy") and sql_metrics.get("avg_accuracy"):
            rag_acc = rag_metrics["avg_accuracy"]
            sql_acc = sql_metrics["avg_accuracy"]
            
            comparison["accuracy"] = {
                "rag_more_accurate": rag_acc > sql_acc,
                "accuracy_difference": abs(rag_acc - sql_acc),
                "accuracy_ratio": max(rag_acc, sql_acc) / max(min(rag_acc, sql_acc), 0.001)
            }
        
        # Reliability comparison
        rag_error_rate = rag_metrics.get("error_rate", 1)
        sql_error_rate = sql_metrics.get("error_rate", 1)
        
        comparison["reliability"] = {
            "rag_more_reliable": rag_error_rate < sql_error_rate,
            "rag_error_rate": rag_error_rate,
            "sql_error_rate": sql_error_rate
        }
        
        # Overall performance score
        def calculate_score(metrics):
            # Weighted scoring: 40% accuracy, 30% speed, 30% reliability
            accuracy_score = metrics.get("avg_accuracy", 0) * 0.4
            
            # Speed score (inverse of response time, normalized)
            response_time = metrics.get("avg_response_time", 10)
            speed_score = min(1.0, 2.0 / response_time) * 0.3
            
            # Reliability score (inverse of error rate)
            reliability_score = (1 - metrics.get("error_rate", 1)) * 0.3
            
            return accuracy_score + speed_score + reliability_score
        
        rag_score = calculate_score(rag_metrics)
        sql_score = calculate_score(sql_metrics)
        
        comparison["overall"] = {
            "rag_score": rag_score,
            "sql_score": sql_score,
            "winner": "RAG" if rag_score > sql_score else "SQL Agent"
        }
        
        return comparison
    
    def _generate_recommendations(self, comparison: Dict) -> List[str]:
        """Generate recommendations based on comparison results"""
        
        recommendations = []
        
        # Speed recommendations
        if comparison.get("response_time", {}).get("rag_faster"):
            recommendations.append("✓ RAG system is faster - consider for real-time applications")
        else:
            recommendations.append("✓ SQL Agent is faster - better for time-sensitive queries")
        
        # Accuracy recommendations
        if comparison.get("accuracy", {}).get("rag_more_accurate"):
            recommendations.append("✓ RAG system is more accurate - better for exploratory queries")
        else:
            recommendations.append("✓ SQL Agent is more accurate - better for precise data retrieval")
        
        # Reliability recommendations
        if comparison.get("reliability", {}).get("rag_more_reliable"):
            recommendations.append("✓ RAG system is more reliable - fewer errors")
        else:
            recommendations.append("✓ SQL Agent is more reliable - fewer failures")
        
        # Overall recommendation
        winner = comparison.get("overall", {}).get("winner", "Unknown")
        recommendations.append(f"🏆 Overall winner: {winner}")
        
        # Use case recommendations
        recommendations.extend([
            "",
            "📋 Use Case Recommendations:",
            "• RAG System: Best for exploratory queries, business context questions, and when SQL expertise is limited",
            "• SQL Agent: Best for precise data retrieval, complex analytics, and when SQL accuracy is critical",
            "• Hybrid Approach: Consider using both systems based on query type and user expertise"
        ])
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a comprehensive comparison report"""
        
        analysis = self.comparison_results["detailed_analysis"]
        
        report = f"""
# RAG vs SQL Agent Performance Comparison Report

**Generated:** {self.comparison_results['timestamp']}

## Executive Summary

This report compares the performance of a Retrieval-Augmented Generation (RAG) system 
against a SQL Agent system for querying the Chinook music database.

## Test Results Overview

### RAG System Performance
- **Total Questions:** {analysis['rag_metrics']['total_questions']}
- **Valid Responses:** {analysis['rag_metrics']['valid_responses']}
- **Error Rate:** {analysis['rag_metrics']['error_rate']:.2%}
- **Average Response Time:** {analysis['rag_metrics']['avg_response_time']:.2f}s
- **Average Accuracy:** {analysis['rag_metrics']['avg_accuracy']:.2%}
- **Average Confidence:** {analysis['rag_metrics'].get('avg_confidence_score', 0):.2f}

### SQL Agent Performance
- **Total Questions:** {analysis['sql_metrics']['total_questions']}
- **Valid Responses:** {analysis['sql_metrics']['valid_responses']}
- **Error Rate:** {analysis['sql_metrics']['error_rate']:.2%}
- **Average Response Time:** {analysis['sql_metrics']['avg_response_time']:.2f}s
- **Average Accuracy:** {analysis['sql_metrics']['avg_accuracy']:.2%}
- **Average Tool Calls:** {analysis['sql_metrics'].get('avg_tool_calls', 0):.1f}

## Comparative Analysis

### Performance Winner: {analysis['comparison']['overall']['winner']}

### Key Findings:
"""
        
        # Add speed comparison
        if analysis['comparison'].get('response_time'):
            speed_comp = analysis['comparison']['response_time']
            faster_system = "RAG" if speed_comp['rag_faster'] else "SQL Agent"
            report += f"- **Speed:** {faster_system} is {speed_comp['speed_ratio']:.1f}x faster\n"
        
        # Add accuracy comparison
        if analysis['comparison'].get('accuracy'):
            acc_comp = analysis['comparison']['accuracy']
            more_accurate = "RAG" if acc_comp['rag_more_accurate'] else "SQL Agent"
            report += f"- **Accuracy:** {more_accurate} is {acc_comp['accuracy_difference']:.1%} more accurate\n"
        
        # Add reliability comparison
        rel_comp = analysis['comparison']['reliability']
        more_reliable = "RAG" if rel_comp['rag_more_reliable'] else "SQL Agent"
        report += f"- **Reliability:** {more_reliable} has lower error rate\n"
        
        # Add recommendations
        report += f"\n## Recommendations\n\n"
        for rec in analysis['recommendations']:
            report += f"{rec}\n"
        
        # Add detailed results
        report += f"\n## Detailed Test Results\n\n"
        report += f"### Sample Question Results\n\n"
        
        # Show first few results as examples
        for i, (rag_result, sql_result) in enumerate(zip(
            self.comparison_results['rag_results'][:3],
            self.comparison_results['sql_results'][:3]
        )):
            report += f"**Question {i+1}:** {rag_result['question']}\n\n"
            report += f"*RAG Answer:* {rag_result['answer'][:200]}...\n"
            report += f"*RAG Time:* {rag_result['response_time']:.2f}s\n\n"
            report += f"*SQL Answer:* {sql_result['answer'][:200]}...\n"
            report += f"*SQL Time:* {sql_result['response_time']:.2f}s\n\n"
            report += "---\n\n"
        
        return report
    
    def save_results(self, filename: str = None):
        """Save comparison results to JSON file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.comparison_results, f, indent=2, default=str)
        
        print(f"Results saved to {filename}")
        return filename

def main():
    """Main function to run the comparison"""
    
    # Get test questions
    test_questions = get_sample_questions(10)  # Test with 10 questions
    
    print("Starting comprehensive comparison...")
    print(f"Test questions: {len(test_questions)}")
    
    # Run comparison
    comparison = ComprehensiveComparison()
    results = comparison.run_performance_tests(test_questions)
    analysis = comparison.analyze_results()
    
    # Generate and display report
    report = comparison.generate_report()
    print("\n" + "="*80)
    print("FINAL REPORT")
    print("="*80)
    print(report)
    
    # Save results
    filename = comparison.save_results()
    
    print(f"\nComparison complete! Results saved to {filename}")

if __name__ == "__main__":
    main() 